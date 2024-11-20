#!/bin/bash

# Script to create a `samba-flask` user and configure sudoers for Samba commands

USER="samba-flask"
SUDOERS_FILE="/etc/sudoers.d/samba-flask"
COMMANDS=(
    "/usr/sbin/useradd"
    "/usr/sbin/usermod"
    "/usr/bin/smbpasswd"
)

echo "Setting up the 'samba-flask' user for Samba Flask application..."

# Check if the user exists
if id "$USER" &>/dev/null; then
    echo "User '$USER' already exists."
else
    echo "Creating user '$USER'..."
    sudo useradd -m -s /bin/bash "$USER"
    if [ $? -eq 0 ]; then
        echo "User '$USER' created successfully."
    else
        echo "Failed to create user '$USER'. Exiting."
        exit 1
    fi
fi

# Check if the sudoers file exists
if [ ! -f "$SUDOERS_FILE" ]; then
    echo "Creating sudoers file for '$USER' at '$SUDOERS_FILE'..."
    echo "$USER ALL=(ALL) NOPASSWD: ${COMMANDS[*]}" | sudo tee "$SUDOERS_FILE" > /dev/null
    if [ $? -eq 0 ]; then
        echo "Sudoers file created successfully."
    else
        echo "Failed to create sudoers file. Exiting."
        exit 1
    fi
else
    echo "Sudoers file for '$USER' already exists."
fi

# Verify sudoers file syntax
sudo visudo -cf "$SUDOERS_FILE"
if [ $? -eq 0 ]; then
    echo "Sudoers file syntax is valid."
else
    echo "Sudoers file syntax is invalid. Please check '$SUDOERS_FILE'."
    exit 1
fi

echo "Setup complete. The 'samba-flask' user can now execute Samba-related commands without a password."
