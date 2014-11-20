# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

NUM_CONTROLLERS = ENV['URSULA_NUM_CONTROLLERS'] || 2
NUM_COMPUTES = ENV['URSULA_NUM_COMPUTES'] || 1
NUM_SWIFT_NODES = ENV['URSULA_NUM_SWIFT_NODES'] || 3
BOX_URL = ENV['URSULA_BOX_URL'] || 'http://apt.openstack.blueboxgrid.com/vagrant/ursula-precise.box'

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  if Vagrant.has_plugin?('vagrant-openstack-provider')
    require 'vagrant-openstack-provider'
    config.vm.provider :openstack do |os, override|
      os.openstack_auth_url = "#{ENV['OS_AUTH_URL']}/tokens"
      os.username           = ENV['OS_USERNAME']
      os.password           = ENV['OS_PASSWORD']
      os.tenant_name        = ENV['OS_TENANT_NAME']
      os.flavor             = 'm1.small'
      os.image              = 'ubuntu-14.04'
      os.openstack_network_url = ENV['OS_NEUTRON_URL'] if ENV['OS_NEUTRON_URL']
      os.networks           =  ['internal']
      os.security_groups    = ['vagrant']
      os.floating_ip_pool   = 'external'
      override.vm.box       = 'openstack'
      override.ssh.username = 'ubuntu'
    end
  end

  config.ssh.forward_agent = true

  config.vm.define "workstation" do |workstation_config|
    workstation_config.vm.box = "ursula-precise"
    workstation_config.vm.box_url = BOX_URL
    workstation_config.vm.hostname = "workstation"
    workstation_config.vm.provider "virtualbox" do |v|
      v.memory = 1024
    end
    if File.exist?("#{ENV['HOME']}/.stackrc")
      config.vm.provision "file", source: "~/.stackrc", destination: ".stackrc"
    end
  end

  config.vm.define "allinone" do |allinone_config|
    allinone_config.vm.box = "ursula-precise"
    allinone_config.vm.box_url = BOX_URL
    allinone_config.vm.hostname = "allinone"
    allinone_config.vm.network :private_network, ip: "172.16.0.100", :netmask => "255.255.255.0"
    allinone_config.vm.network :private_network, ip: "192.168.255.100", :netmask => "255.255.255.0"
    allinone_config.vm.provider "virtualbox" do |v|
      v.memory = 4096
      v.cpus = 2
      v.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
    end
  end

  config.vm.define "allinone" do |allinone_config|
    allinone_config.vm.box = "ursula-precise"
    allinone_config.vm.box_url = BOX_URL
    allinone_config.vm.hostname = "allinone"
    allinone_config.vm.network :private_network, ip: "172.16.0.100", :netmask => "255.255.255.0"
    allinone_config.vm.network :private_network, ip: "192.168.255.100", :netmask => "255.255.255.0"
    allinone_config.vm.provider "virtualbox" do |v|
      v.memory = 4096
      v.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
    end
  end

  (1..NUM_CONTROLLERS).each do |i|
    config.vm.define "controller#{i}" do |controller_config|
      controller_config.vm.box = "ursula-precise"
      controller_config.vm.box_url = BOX_URL
      controller_config.vm.hostname = "controller#{i}"
      controller_config.vm.network :private_network, ip: "172.16.0.10#{i}", :netmask => "255.255.255.0"
      controller_config.vm.network :private_network, ip: "192.168.254.10#{i}", :netmask => "255.255.255.0"
      controller_config.vm.provider "virtualbox" do |v|
        v.memory = 2048
        v.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
      end
    end
  end

  (1..NUM_COMPUTES).each do |i|
    config.vm.define "compute#{i}" do |compute_config|
      compute_config.vm.box = "ursula-precise"
      compute_config.vm.box_url = BOX_URL
      compute_config.vm.hostname = "compute#{i}"
      compute_config.vm.network :private_network, ip: "172.16.0.11#{i}", :netmask => "255.255.255.0"
      compute_config.vm.network :private_network, ip: "192.168.254.11#{i}", :netmask => "255.255.255.0"
      compute_config.vm.provider "virtualbox" do |v|
        v.memory = 1536
        v.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
      end
    end
  end

  (1..NUM_SWIFT_NODES).each do |i|
    file_to_disk = "proxy#{i}.1.vdi"
    config.vm.define "swiftnode#{i}" do |swiftnode_config|
      swiftnode_config.vm.provider "virtualbox" do |v|
        v.customize ['createhd', '--filename', file_to_disk, '--size', 1024]
        v.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', 1, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
      end
      swiftnode_config.vm.box = "ursula-precise"
      swiftnode_config.vm.box_url = BOX_URL
      swiftnode_config.vm.hostname = "swift#{i}"
      swiftnode_config.vm.network :private_network, ip: "10.1.1.13#{i}", :netmask => "255.255.0.0"
      swiftnode_config.vm.provider "virtualbox" do |v|
        v.memory = 768
      end
    end
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbooks/vagrant/bootstrap.yml"
    ansible.sudo = true
    ansible.groups = {
      "controller" => ["controller1", "controller2", "allinone"],
      "compute" => ["compute1", "allinone"],
      "workstation" => ["workstation"],
      "openstack:children" => ["controller", "compute", "allinone"],
      "all_groups:children" => ["controller", "compute", "workstation"]
    }
  end

end
