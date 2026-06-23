
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, LogInfo, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python import get_package_share_directory
import re
import os

environment = ['ocean_environment', 'pool_environment']
selected_environment = environment[0]  # Change index to switch environment
ENVIRONMENT = selected_environment



def parse_scenario_info(pkg_dir):
    """Parse the ocean environment SCN and included robot SCN to extract debug info."""
    info = {
        'environment_scn': f'{ENVIRONMENT}.scn',
        'included_scn': 'UNKNOWN',
        'vehicle_name': 'UNKNOWN',
        'position': 'UNKNOWN',
        'robot_name': 'UNKNOWN',
        'robot_type': 'UNKNOWN',
        'physics_type': 'UNKNOWN',
        'physical_mesh': 'UNKNOWN',
        'visual_mesh': 'UNKNOWN',
        'mass': 'UNKNOWN',
    }

    env_path = os.path.join(pkg_dir, 'scenarios', f'{ENVIRONMENT}.scn')

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()

        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith('<include') and 'file=' in stripped:
                match = re.search(r'scenarios/([^"\']+\.scn)', stripped)
                if match:
                    info['included_scn'] = match.group(1)

            if 'vehicle_name' in line and 'value=' in line and not stripped.startswith('<!--'):
                match = re.search(r'name="vehicle_name"\s+value="([^"]+)"', line)
                if match:
                    info['vehicle_name'] = match.group(1)

            if 'name="position"' in line and 'value=' in line and not stripped.startswith('<!--'):
                match = re.search(r'name="position"\s+value="([^"]+)"', line)
                if match:
                    info['position'] = match.group(1)

    if info['included_scn'] != 'UNKNOWN':
        robot_path = os.path.join(pkg_dir, 'scenarios', info['included_scn'])

        if os.path.exists(robot_path):
            with open(robot_path, 'r') as f:
                robot_content = f.read()

            match = re.search(r'<robot\s+name="([^"]+)"', robot_content)
            if match:
                info['robot_name'] = match.group(1)

            match = re.search(
                r'<base_link[^>]*type="([^"]+)"[^>]*physics="([^"]+)"',
                robot_content
            )
            if match:
                info['robot_type'] = match.group(1)
                info['physics_type'] = match.group(2)

            in_physical = False
            for line in robot_content.splitlines():
                if '<physical>' in line:
                    in_physical = True

                if in_physical and 'mesh filename=' in line:
                    match = re.search(r'mesh filename="([^"]+)"', line)
                    if match:
                        info['physical_mesh'] = os.path.basename(match.group(1))
                    in_physical = False

                if '</physical>' in line:
                    in_physical = False

            in_visual = False
            for line in robot_content.splitlines():
                if '<visual>' in line:
                    in_visual = True

                if in_visual and 'mesh filename=' in line:
                    match = re.search(r'mesh filename="([^"]+)"', line)
                    if match:
                        info['visual_mesh'] = os.path.basename(match.group(1))
                    in_visual = False

                if '</visual>' in line:
                    in_visual = False

            match = re.search(r'<mass value="([^"]+)"', robot_content)
            if match:
                info['mass'] = match.group(1) + ' kg'

    return info


def generate_launch_description():
    pkg_dir = get_package_share_directory('stonefish_qut_rov')
    info = parse_scenario_info(pkg_dir)

    stonefish_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            get_package_share_directory('stonefish_ros2') +
            '/launch/stonefish_simulator.launch.py'
        ),
        launch_arguments={
            'simulation_data': pkg_dir,
            'scenario_desc': pkg_dir + f'/scenarios/{ENVIRONMENT}.scn',
            'simulation_rate': '500.0',
            'window_res_x': '920',
            'window_res_y': '1000',
            'rendering_quality': 'high',
        }.items()
    )

    delayed_debug_print = TimerAction(
        period=8.0,
        actions=[
            LogInfo(msg=['']),
            LogInfo(msg=['============================================================']),
            LogInfo(msg=['               STONEFISH LAUNCH CONFIGURATION              ']),
            LogInfo(msg=['============================================================']),
            LogInfo(msg=[f"  Environment SCN : {info['environment_scn']}"]),
            LogInfo(msg=[f"  Included SCN    : {info['included_scn']}"]),
            LogInfo(msg=['------------------------------------------------------------']),
            LogInfo(msg=[f"  Vehicle Name    : {info['vehicle_name']}"]),
            LogInfo(msg=[f"  Spawn Position  : {info['position']}"]),
            LogInfo(msg=['------------------------------------------------------------']),
            LogInfo(msg=[f"  Robot Name      : {info['robot_name']}"]),
            LogInfo(msg=[f"  Base Link Type  : {info['robot_type']}"]),
            LogInfo(msg=[f"  Physics Type    : {info['physics_type']}"]),
            LogInfo(msg=[f"  Physical Mesh   : {info['physical_mesh']}"]),
            LogInfo(msg=[f"  Visual Mesh     : {info['visual_mesh']}"]),
            LogInfo(msg=[f"  Mass            : {info['mass']}"]),
            LogInfo(msg=[f"  SCN Path Used   : {pkg_dir}/scenarios/{ENVIRONMENT}.scn"]),
            LogInfo(msg=['============================================================']),
            LogInfo(msg=['']),
        ]
    )

    return LaunchDescription([
        stonefish_launch,
        delayed_debug_print,
    ])