#!/usr/bin/bash
#
# Creates necessary directories and configuration for nice-bot.
#

if [[ "$EUID" -ne 0 ]]; then
	echo "Script must be executed as sudo"
	exit 1
fi

# Get directory of this file
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Create necessary directories
INSTALL_DIRS=("/var/lib/nice-bot" "/var/log/nice-bot" "/etc/nice-bot")
echo mkdir -q "${INSTALL_DIRS[@]}"

# Ask for token and write config
echo -n "Write Bot Token: " && read -r token
sed -e "s/token = ''/token ='$token'/" "$DIR/../bot/config/config.toml" > /etc/nice-bot/config.toml

# Give permissions to normal user 
chown -R "$SUDO_USER" "${INSTALL_DIRS[@]}"

# Exit
echo "Config at /etc/nice-bot/config.toml"
echo "Done"
exit 0
