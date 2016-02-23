require 'spec_helper'

describe file('/var/lib/libvirt/images') do
  it { should be_mode 711 }
end

describe file('/dev/kvm') do
  it { should exist }
  it { should be_mode 660 }
end 

describe file('/etc/libvirt/libvirtd.conf') do
  file_contents = ['^unix_sock_group = "libvirtd"',
                   '^unix_sock_ro_perms = "0777"',
                   '^unix_sock_rw_perms = "0770"']
  file_contents.each do |file_line|
    it { should contain file_line }
  end
end

describe file('/etc/libvirt/libvirtd.conf') do
  it { should contain "^listen_tls = 0" }
  it { should contain "^listen_tcp = 1" }
end

describe file('/etc/libvirt/qemu.conf') do
  file_contents = ['^vnc_listen = "0.0.0.0"',
                   '^user = "qemu"   # A user named "qemu"',
                   '^user = "+0"     # Super user (uid=0)',
                   '^user = "100"    # A user named "100" or a user with uid=100',
                   '^user = "root"']
  file_contents.each do |file_line|
    it { should_not contain file_line }
  end
end   
