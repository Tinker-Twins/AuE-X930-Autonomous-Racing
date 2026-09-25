# Notes for NeoRacer

## Resources:

- Documentation: https://neobotics.org/docs

- Setup & Testing: https://neobotics.org/docs/getting-started/unbox

- Networking: https://neobotics.org/docs/software/networking

- Remote Desktop: https://neobotics.org/docs/software/remote-desktop

## Tips:

- Some screws can be difficult to install, try magnetizing the hex key for ease.

- Attach the WiFi antennas to the chassis using zip ties before connecting them to the Jetson Wi-Fi card. Once the top platform is disassembled, Jetson WiFi card is accessible from the bottom.

- Before installing the `neoracer_ros2_driver`, unmask the NVIDIA camera service:
    ```bash
    sudo systemctl unmask nvargus-daemon
    ```

- At least for the very first time you boot the vehicle, you will need a monitor with HDMI cable, and a USB keyboard/mouse to work with the vehicle. You can then choose to set up Remote Desktop via vehicle's router hotspot for later use.

## Safety:

- Operate the vehicle ONLY in open/uncrowded spaces, with at least one dedicated person operating the remote controller for manual override.

- The vehicle speed in autonomous mode is regulated to 6 m/s for safety.

- NEVER leave the vehicle powered unattended.

- Do NOT let your vehicle's LiPo battery reach a state of deep discharge (when its voltage drops below the safe minimum threshold of 3.0 volts per cell). Stop and charge your battery when the vehicle starts making a beeping sound!

- Configure the charger before plugging the battery in for charging.

- ⁠The battery charger is ill-designed, make sure to insert the `balance terminal` (4-pin) correctly (since it can go in either way).

- NEVER leave batteries on charging unattended.

- While charging the batteries, make sure to keep the equipment in relatively open/uncrowded spaces and nowhere near any flammable  substances.

- Do NOT charge batteries if you observe any abnormality (puffing, heating, odor, smoke, etc.).

- Do NOT charge the batteries while the discharge terminal is plugged in.