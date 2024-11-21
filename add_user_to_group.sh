#!/bin/bash

# Define the group name
GROUP_NAME="storageuser"

# Check if the group already exists
if getent group "$GROUP_NAME" > /dev/null; then
    echo "Group '$GROUP_NAME' already exists."
else
    # Create the group
    sudo groupadd "$GROUP_NAME"
    echo "Group '$GROUP_NAME' created."
fi

# Get a list of all regular users
# Exclude system users with UID < 1000
USERS=$(awk -F: '$3 >= 1000 {print $1}' /etc/passwd)

# Add each user to the group
for USER in $USERS; do
    sudo usermod -aG "$GROUP_NAME" "$USER"
    echo "Added user '$USER' to group '$GROUP_NAME'."
done

echo "All users have been added to the group '$GROUP_NAME'."
