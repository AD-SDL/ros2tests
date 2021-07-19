from setuptools import setup
import os
from glob import glob

package_name = "arm_controller"

setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="nerra",
    maintainer_email="alan.linghao.wang@gmail.com",
    description="TODO: Package description",
    license="TODO: License declaration",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "arm_manager = arm_controller.armManager:main",
            "arm_transfer_handler = arm_controller.armTransferHandler:main",
        ],
    },
)