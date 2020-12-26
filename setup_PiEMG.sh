#Get updates and upgrades
echo "Getting update"
sudo apt-get update -y

echo "Getting upgrade"
sudo apt-get upgrade -y

echo "Getting pip-3.2"
sudo apt-get install python3-pip -y

echo "Getting Python SPI wrapper"
sudo pip-3.2 install spidev

echo "Getting pigpio"
wget abyz.co.uk/rpi/pigpio/pigpio.zip
unzip pigpio.zip
cd PIGPIO
sudo make
sudo make install
sudo python3 setup.py install
cd ..

echo "Creating Desktop Folder"
sudo mkdir /home/pi/Desktop

echo "Moving EMG_Acquire.py to Desktop"
sudo cp EMG_Acquire.py /home/pi/Desktop/EMG_Acquire.py

echo "Cleaning Up"
sudo rm PIGPIO -r
sudo rm pigpio.zip