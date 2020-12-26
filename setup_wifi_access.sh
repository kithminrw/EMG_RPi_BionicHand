#Get hostapd
echo "Getting hostapd isc-dhcp-server"
sudo apt-get install hostapd isc-dhcp-server

echo "Updating /etc/dhcp/dhcp.conf file"
sudo cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.old
sudo cp dhcpd.conf /etc/dhcp/dhcpd.conf

echo "Updating /etc/default/isc-dhcp-server"
sudo cp /etc/default/isc-dhcp-server /etc/default/isc-dhcp-server.old
sudo cp isc-dhcp-server /etc/default/isc-dhcp-server

echo "Shutting Down wlan0"
sudo ifdown wlan0

echo "Updating /etc/network/interfaces"
sudo cp /etc/network/interfaces /etc/network/interfaces.old
sudo cp interfaces /etc/network/interfaces

echo "Assigning wlan0 to 192.168.42.1"
sudo ifconfig wlan0 192.168.42.1

echo "Creating /etc/hostapd/hostapd.conf"
sudo cp hostapd.conf /etc/hostapd/hostapd.conf

echo "Updating /etc/default/hostapd"
sudo cp /etc/default/hostapd /etc/default/hostapd.old
sudo cp hostapd /etc/default/hostapd

echo "Updating /etc/sysctl.conf"
sudo cp /etc/sysctl.conf /etc/sysctl.conf.old
sudo cp sysctl.conf /etc/sysctl.conf

echo "Starting port forwarding"
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

echo "Creating network translation between eth0 and wlan0"
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

echo "Adding translation to bootup"
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

echo "Updating /etc/network/interfaces"
#Not necessary again since we did it already...

echo "Updating hostapd"
#wget http://adafruit-download.s3.amazonaws.com/adafruit_hostapd_14128.zip
#unzip adafruit_hostapd_14128.zip
sudo mv /usr/sbin/hostapd /usr/sbin/hostapd.ORIG
sudo cp hostapd_binary /usr/sbin/hostapd
sudo chmod 755 /usr/sbin/hostapd

echo "Starting Services"
sudo service hostapd start 
sudo service isc-dhcp-server start

echo "Starting daemon services"
sudo update-rc.d hostapd enable 
sudo update-rc.d isc-dhcp-server enable

echo "Removing WPA-Supplicant"
sudo rm /usr/share/dbus-1/system-services/fi.w1.wpa_supplicant1.service

echo "Setup Complete! Please reboot!"