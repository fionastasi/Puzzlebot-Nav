# Guía de Migración: Simulación → Robot Físico
**Puzzlebot · ROS 2 Humble · Nav2 + SLAM Toolbox**  
Equipo Ubuntufílicos — Fiona Stasi, Daniel de Regules, Alejandro Araiza

---

## Índice
1. [Arquitectura general](#1-arquitectura-general)
2. [Requisitos e instalación](#2-requisitos-e-instalación)
3. [Hardware y puertos seriales](#3-hardware-y-puertos-seriales)
4. [Qué corre en cada máquina](#4-qué-corre-en-cada-máquina)
5. [Modo SLAM — generar un mapa](#5-modo-slam--generar-un-mapa)
6. [Modo Navegación autónoma](#6-modo-navegación-autónoma)
7. [Nodos propios — código y lógica](#7-nodos-propios--código-y-lógica)
8. [Parámetros: simulación vs robot real](#8-parámetros-simulación-vs-robot-real)
9. [Diferencias clave del URDF en hardware real](#9-diferencias-clave-del-urdf-en-hardware-real)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Arquitectura general

El proyecto separa estrictamente simulación de hardware real. El paquete `puzzlebot_real_robot` reemplaza **solo** la capa que en simulación provee Gazebo: no toca Nav2 ni el URDF.

```
┌─────────────────────────────────────────────────────┐
│              puzzlebot_description                  │
│       URDF/Xacro · meshes · TF tree estático        │
│          (compartido sim y robot real)               │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐   ┌──────────▼──────────────────┐
│ puzzlebot_gazebo │   │    puzzlebot_real_robot       │
│  (solo sim)      │   │  micro-ROS · RPLidar · odom  │
│  Gazebo + bridge │   │  joint_states · TF dinámico  │
└───────┬──────────┘   └──────────┬──────────────────┘
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   puzzlebot_navigation2  │
        │  Nav2 · AMCL · SLAM      │
        │  costmaps · planners     │
        └─────────────────────────┘
```

### Topic graph (robot real)

```
micro-ROS (MCU)
  ├─ publica → /VelocityEncR  (Float32, BEST_EFFORT)
  ├─ publica → /VelocityEncL  (Float32, BEST_EFFORT)
  └─ suscribe ← /cmd_vel

puzzlebot_localization.py
  ├─ suscribe ← /VelocityEncR, /VelocityEncL
  └─ publica → /odom  (Odometry, 100 Hz)

puzzlebot_joint_state_publisher.py
  ├─ suscribe ← /odom
  ├─ publica → /joint_states  (JointState, 100 Hz)
  └─ broadcast TF: odom → base_footprint

rplidar_node
  └─ publica → /scan  (LaserScan, frame: laser_frame)

robot_state_publisher
  └─ broadcast TF estático: base_footprint → base_link → lidar_base_link → laser_frame

slam_toolbox / nav2_bringup   (laptop)
  ├─ suscribe ← /scan, /odom, /tf
  └─ publica → /map, /cmd_vel, /tf (map → odom)
```

---

## 2. Requisitos e instalación

### En ambas máquinas

```bash
# ROS 2 Humble
sudo apt install ros-humble-desktop

# Dependencias del workspace
sudo apt install \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-robot-state-publisher \
  ros-humble-xacro \
  ros-humble-teleop-twist-keyboard \
  python3-colcon-common-extensions
```

### Solo en el Jetson (robot)

```bash
sudo apt install ros-humble-rplidar-ros

# Si el Jetson no tiene internet en la pista, descarga en laptop y transfiere:
# [en laptop con internet]
apt-get download ros-humble-xacro ros-humble-rplidar-ros

# [transfiere al Jetson]
scp ros-humble-*.deb puzzlebot@<IP_JETSON>:~/

# [en el Jetson]
sudo dpkg -i ros-humble-xacro_*.deb
sudo dpkg -i ros-humble-rplidar-ros_*.deb
```

### Compilar el workspace

```bash
cd ~/puzzlebot_nv_ws    # o la ruta donde tengas el ws

# Ignora los paquetes de sim si estás en el Jetson (no tiene Gazebo)
colcon build --packages-ignore puzzlebot_gazebo

source install/setup.bash
```

> **Tip:** agrega `source ~/puzzlebot_nv_ws/install/setup.bash` a tu `~/.bashrc` en ambas máquinas.

---

## 3. Hardware y puertos seriales

### Dispositivos conectados al Jetson

| Dispositivo | Chip serial | Puerto default | Symlink fijo |
|---|---|---|---|
| RPLidar A1 | CP2102 (serial: `0001`) | `/dev/ttyUSB?` | `/dev/rplidar` |
| MCU (micro-ROS) | CP2102 (serial único) | `/dev/ttyUSB?` | `/dev/microros` |

### Por qué los puertos cambian

El Jetson reasigna `/dev/ttyUSBx` según el orden de detección. Ambos dispositivos usan el **mismo chip** (CP2102, `idVendor=10c4 idProduct=ea60`), así que no se distinguen por vendor/product — solo por número de serie.

### Identificar los seriales

```bash
# Con el dispositivo conectado:
udevadm info -a -n /dev/ttyUSB0 | grep -E "idVendor|idProduct|serial"
# Repite para ttyUSB1
```

### Crear reglas udev permanentes

```bash
sudo nano /etc/udev/rules.d/99-puzzlebot.rules
```

```udev
# RPLidar A1
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", \
  ATTRS{serial}=="0001", SYMLINK+="rplidar", MODE="0666"

# micro-ROS MCU  (sustituye con el serial real de tu Jetson)
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", \
  ATTRS{serial}=="b4f8115b2fffec118af66f508ce70331", SYMLINK+="microros", MODE="0666"
```

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

El `MODE="0666"` elimina la necesidad de `sudo chmod 666 /dev/ttyUSB*` en cada arranque.

### Actualizar el launch con el symlink

En [real_robot_core.launch.xml](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_real_robot/launch/real_robot_core.launch.xml), cambia el puerto del LiDAR al symlink fijo:

```xml
<!-- Antes (inestable): -->
<arg name="serial_port" value="/dev/ttyUSB1" />

<!-- Después (estable): -->
<arg name="serial_port" value="/dev/rplidar" />
```

---

## 4. Qué corre en cada máquina

### Resumen rápido

| Launch file | Máquina | Cuándo |
|---|---|---|
| `real_robot_core.launch.xml` | **Jetson** | Siempre — bringup de hardware |
| `real_robot_slam.launch.xml` | **Laptop** | Fase 1: generar mapa |
| `real_robot_nav2.launch.xml` | **Laptop** | Fase 2: navegación autónoma |

### Requisito de red

Ambas máquinas deben estar en la **misma red WiFi** con el mismo `ROS_DOMAIN_ID`:

```bash
# Mismo valor en Jetson y laptop
export ROS_DOMAIN_ID=0
```

Verifica conectividad:

```bash
# En laptop — debe ver los topics publicados por el Jetson:
ros2 topic list
ros2 topic echo /odom
ros2 topic echo /scan
```

---

## 5. Modo SLAM — generar un mapa

### Paso 1 — Jetson: levantar el hardware

```bash
# En el Jetson
source ~/puzzlebot_nv_ws/install/setup.bash
ros2 launch puzzlebot_real_robot real_robot_core.launch.xml
```

Nodos que inician:
- `robot_state_publisher` — TF estático del URDF
- `micro_ros_agent` — bridge MCU ↔ ROS 2
- `rplidar_node` — publica `/scan` en `laser_frame`
- `puzzlebot_localization` — publica `/odom` a 100 Hz
- `puzzlebot_joint_state_publisher` — publica `/joint_states` + TF `odom→base_footprint`

Verifica antes de continuar:

```bash
# Desde laptop
ros2 topic hz /scan          # ~7-10 Hz para RPLidar A1
ros2 topic hz /odom          # ~100 Hz
ros2 topic echo /odom --once # debe tener frame_id: "odom", child: "base_footprint"
```

### Paso 2 — Laptop: lanzar SLAM

```bash
# En la laptop
source ~/puzzlebot_nv_ws/install/setup.bash
ros2 launch puzzlebot_real_robot real_robot_slam.launch.xml
```

Nodos que inician:
- `robot_state_publisher` — copia local del TF estático (necesario para RViz)
- `async_slam_toolbox_node` — SLAM con cierre de bucle
- `rviz2` — visualización del mapa en construcción
- `teleop_twist_keyboard` — control manual (en ventana `xterm`)

### Paso 3 — Mover el robot y guardar el mapa

1. En la ventana de teleop, mueve el robot **lentamente** por toda la pista.
2. Cubre todas las zonas; el mapa mejora con múltiples pasadas.
3. Cuando el mapa esté completo:

```bash
# Guarda desde la laptop (o el Jetson, lo que tenga el workspace)
ros2 run nav2_map_server map_saver_cli \
  -f ~/puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_real_robot/maps/map_real

# Genera:
#   map_real.pgm  — imagen del mapa
#   map_real.yaml — metadata (resolución, origen, etc.)
```

Rebuild del paquete para que el mapa quede en el install:

```bash
cd ~/puzzlebot_nv_ws
colcon build --packages-select puzzlebot_real_robot
source install/setup.bash
```

---

## 6. Modo Navegación autónoma

### Paso 1 — Jetson: levantar hardware (igual que SLAM)

```bash
ros2 launch puzzlebot_real_robot real_robot_core.launch.xml
```

### Paso 2 — Laptop: lanzar Nav2

```bash
ros2 launch puzzlebot_real_robot real_robot_nav2.launch.xml
```

Para usar un mapa distinto al predeterminado:

```bash
ros2 launch puzzlebot_real_robot real_robot_nav2.launch.xml \
  map_path:=/ruta/absoluta/a/mi_mapa.yaml
```

Nodos que inician:
- `robot_state_publisher` — TF estático local
- Nav2 stack completo: `lifecycle_manager`, `amcl`, `global_costmap`, `local_costmap`, `planner_server`, `controller_server`, `bt_navigator`, `recoveries_server`
- `rviz2` — visualización de costmaps y path

### Paso 3 — Inicializar pose en RViz

1. En RViz, usa **"2D Pose Estimate"** (barra superior) para indicar dónde está el robot en el mapa.
2. Observa cómo las partículas de AMCL convergen.
3. Usa **"2D Goal Pose"** para enviar un objetivo de navegación.

> **Nota:** `set_initial_pose: false` en `nav2_params_real.yaml` — AMCL **no** arranca con pose automática. Siempre debes usar "2D Pose Estimate" manualmente al inicio.

---

## 7. Nodos propios — código y lógica

### `puzzlebot_localization.py` — Odometría por encoders

**Corre en:** Jetson  
**Archivo:** [puzzlebot_real_robot/scripts/puzzlebot_localization.py](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_real_robot/scripts/puzzlebot_localization.py)

Reemplaza el plugin `diff_drive` de Gazebo. Integra las velocidades angulares de los encoders y publica `/odom`.

```python
# Parámetros físicos — deben coincidir con wheels.xacro
WHEEL_RADIUS     = 0.05   # m  (r)
WHEEL_SEPARATION = 0.19   # m  (l)

# Cinemática diferencial directa
v = r * (wr + wl) / 2.0   # velocidad lineal del robot
w = r * (wr - wl) / l     # velocidad angular del robot

# Integración de Euler a 100 Hz
x     += v * cos(theta) * dt
y     += v * sin(theta) * dt
theta += w * dt
```

**QoS crítico:** micro-ROS publica con `BEST_EFFORT`. Si la suscripción usa `RELIABLE` (default de ROS 2), **no llega ningún mensaje**. El nodo ya lo maneja:

```python
qos_sensor = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    depth=10,
)
self.create_subscription(Float32, '/VelocityEncR', self._cb_wr, qos_sensor)
self.create_subscription(Float32, '/VelocityEncL', self._cb_wl, qos_sensor)
```

---

### `puzzlebot_joint_state_publisher.py` — TF dinámico + joint states

**Corre en:** Jetson  
**Archivo:** [puzzlebot_real_robot/scripts/puzzlebot_joint_state_publisher.py](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_real_robot/scripts/puzzlebot_joint_state_publisher.py)

Hace dos cosas:
1. **Publica `/joint_states`** — necesario para que `robot_state_publisher` anime las ruedas en RViz.
2. **Emite el TF `odom → base_footprint`** — fuente única; si existe otra fuente simultánea el árbol de TF se vuelve inconsistente.

```python
# Broadcast del TF en cada mensaje de /odom
t = TransformStamped()
t.header.frame_id = 'odom'
t.child_frame_id  = 'base_footprint'
t.transform.translation.x = msg.pose.pose.position.x
t.transform.translation.y = msg.pose.pose.position.y
t.transform.rotation      = msg.pose.pose.orientation
self.tf_broadcaster.sendTransform(t)

# Nombres de joints deben coincidir con wheels.xacro
js.name = ['left_wheel_joint', 'right_wheel_joint']
```

---

## 8. Parámetros: simulación vs robot real

### Diferencias principales

| Parámetro | Simulación | Robot real | Motivo |
|---|---|---|---|
| `use_sim_time` | `true` | `false` | El robot usa reloj del sistema, no `/clock` de Gazebo |
| `base_frame` (SLAM) | `base_link` | `base_footprint` | El TF real se ancla en `base_footprint` |
| `transform_tolerance` | `0.2 s` | `0.5 s` | El TF real tiene mayor latencia de red |
| `max_beams` (AMCL) | `36` | `120` | El RPLidar A1 real tiene barrido completo de 360° |
| `update_min_a / _d` | `0.2 / 0.25` | `0.02 / 0.02` | Actualizaciones frecuentes compensan la deriva del encoder |
| `controller_frequency` | `20.0 Hz` | `10.0 Hz` | Frecuencia segura para el hardware |
| `desired_linear_vel` | `0.15 m/s` | `0.10 m/s` | Velocidad conservadora en pista física |
| `footprint` | `robot_radius` | polígono explícito | Huella precisa para evitar colisiones reales |
| `max_laser_range` | `12.0 m` | `8.0 m` | Rango real del RPLidar A1 |

### `slam_toolbox_real.yaml` — diferencias clave

```yaml
slam_toolbox:
  ros__parameters:
    use_sim_time: false
    base_frame: base_footprint        # base_link en simulación
    max_laser_range: 8.0              # 12.0 en simulación
    do_loop_closing: true
    solver_plugin: solver_plugins::CeresSolver
    ceres_linear_solver: SPARSE_NORMAL_CHOLESKY
    transform_timeout: 0.5            # tolera latencia de red
    minimum_travel_distance: 0.12     # actualiza con movimientos pequeños
    minimum_travel_heading: 0.17
```

### `nav2_params_real.yaml` — diferencias clave

```yaml
amcl:
  ros__parameters:
    use_sim_time: false
    base_frame_id: "base_footprint"
    max_beams: 120                    # 36 en simulación
    transform_tolerance: 1.0          # 0.5 en simulación
    update_min_a: 0.02                # 0.2 en simulación
    update_min_d: 0.02                # 0.25 en simulación
    set_initial_pose: false           # pose manual con RViz
```

---

## 9. Diferencias clave del URDF en hardware real

### Por qué se usa `puzzlebot.urdf.xacro` y no `puzzlebot.xacro`

`puzzlebot.xacro` siempre incluye `puzzlebot_control.xacro`, que contiene plugins de Gazebo (`gz-sim-diff-drive-system`, `gz-sim-joint-state-publisher-system`, `gz-sim-sensors-system`). En hardware real estos plugins no hacen nada, pero en versiones antiguas de `robot_state_publisher` pueden causar advertencias o fallos.

El bringup real apunta directamente al URDF limpio:

```xml
<!-- real_robot_core.launch.xml -->
<let name="urdf_path"
     value="$(find-pkg-share puzzlebot_description)/urdf/puzzlebot.urdf.xacro" />

<node pkg="robot_state_publisher" exec="robot_state_publisher" output="screen">
  <param name="robot_description" value="$(command 'xacro $(var urdf_path)')" />
  <param name="use_sim_time" value="false" />
</node>
```

### Árbol de TF en hardware real

```
map
 └── odom                          ← publicado por slam_toolbox / amcl (laptop)
      └── base_footprint           ← publicado por puzzlebot_joint_state_publisher (Jetson)
           └── base_link           ← estático (robot_state_publisher, URDF)
                └── lidar_base_link
                     └── laser_frame   ← estático (robot_state_publisher, URDF)
```

Regla: **una sola fuente por TF**. Si Gazebo está corriendo y también el nodo de joint states, el árbol se rompe.

---

## 10. Troubleshooting

### El robot no se mueve con teleop

```bash
# Diagnosticar paso a paso:
ros2 node list                    # ¿está vivo el serial_node de micro-ROS?
ros2 topic info /cmd_vel          # ¿hay publishers Y subscribers?
ros2 topic echo /cmd_vel          # ¿llegan comandos del teleop?
ros2 topic echo /odom --once      # ¿responde la odometría?
```

**Causa más común:** el agente de micro-ROS se desconecta silenciosamente. Reinicia `real_robot_core.launch.xml` y verifica que `/VelocityEncR` y `/VelocityEncL` tengan datos:

```bash
ros2 topic echo /VelocityEncR
ros2 topic echo /VelocityEncL
```

### TF tree roto / RViz muestra "No transform from..."

```bash
ros2 run tf2_tools view_frames     # genera frames.pdf con el árbol actual
ros2 run tf2_ros tf2_echo odom base_footprint
```

Causas comunes:
- `use_sim_time: true` en algún nodo del robot real → queda esperando `/clock` que nunca llega.
- Dos nodos publicando el mismo TF (e.g., Gazebo + `puzzlebot_joint_state_publisher` corriendo simultáneamente).

### SLAM no construye el mapa

```bash
ros2 topic hz /scan        # debe ser > 5 Hz
ros2 topic hz /odom        # debe ser ~100 Hz
ros2 run tf2_ros tf2_echo base_footprint laser_frame  # debe resolverse
```

Si `/scan` llega pero el mapa no crece: verifica que `base_frame: base_footprint` en `slam_toolbox_real.yaml` coincida con el `child_frame_id` que publica `/odom`.

### `rplidar_node` no arranca

```bash
ls -la /dev/rplidar        # ¿existe el symlink?
ls -la /dev/ttyUSB*        # ¿está el dispositivo conectado?
```

Si no existe `/dev/rplidar`, las reglas udev no se aplicaron. Recarga:

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
# Desconecta y reconecta el LiDAR físicamente
```

### `xacro` no instalado en el Jetson

```
[robot_state_publisher]: xacro: command not found
```

```bash
# Sin internet en la pista:
# [en laptop con internet]
apt-get download ros-humble-xacro
scp ros-humble-xacro_*.deb puzzlebot@<IP_JETSON>:~/

# [en el Jetson]
sudo dpkg -i ros-humble-xacro_*.deb
```

### AMCL no converge (robot "teletransportado" en RViz)

1. Usa **"2D Pose Estimate"** en RViz para dar la pose inicial manualmente.
2. Mueve el robot ligeramente con teleop — las partículas convergen con el movimiento.
3. Si sigue mal, verifica que el mapa cargado corresponda a la pista actual.

### Nav2 lifecycle nodes no activan

```bash
ros2 lifecycle list /amcl
```

Si los nodos están en estado `unconfigured`, el lifecycle manager no arrancó. Revisa que `autostart: true` esté en `nav2_params_real.yaml` o pásalo como argumento:

```bash
ros2 launch puzzlebot_real_robot real_robot_nav2.launch.xml autostart:=true
```

---

## Referencia rápida de comandos

```bash
# ─── JETSON ─────────────────────────────────────────────
ros2 launch puzzlebot_real_robot real_robot_core.launch.xml

# ─── LAPTOP: SLAM ───────────────────────────────────────
ros2 launch puzzlebot_real_robot real_robot_slam.launch.xml

# Guardar mapa
ros2 run nav2_map_server map_saver_cli \
  -f ~/puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_real_robot/maps/map_real

# ─── LAPTOP: NAVEGACIÓN ─────────────────────────────────
ros2 launch puzzlebot_real_robot real_robot_nav2.launch.xml

# Con mapa alternativo
ros2 launch puzzlebot_real_robot real_robot_nav2.launch.xml \
  map_path:=/ruta/a/mi_mapa.yaml

# ─── DIAGNÓSTICO ─────────────────────────────────────────
ros2 topic list
ros2 topic hz /scan /odom
ros2 run tf2_tools view_frames
ros2 node list
```
