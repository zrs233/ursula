require 'spec_helper'

describe  file('/etc/mongod.conf') do
  it { should be_mode 640 }
  it { should be_owned_by 'mongodb' }
  it { should be_grouped_into 'root' }
end

describe file ('/etc/mongod.conf') do
  it { should contain 'logpath=/var/log/mongodb/mongod.log' }
end

describe file ('/etc/mongod.conf') do
  it { should contain 'logappend=true' }
end

describe file ('/var/lib/mongodb') do
  it { should be_directory }
end

describe file ('/var/lib/mongodb') do
  it { should be_mode 755 }
  it { should be_owned_by 'mongodb' }
  it { should be_grouped_into 'mongodb'}
end

files = Dir.glob("/var/lib/mongodb/local.*")
files.each do |file|
  describe file("#{file}") do
    it { should be_mode 600 }
    it { should be_owned_by 'mongodb' }
    it { should be_grouped_into 'nogroup' }
  end
end

files = Dir.glob("/var/lib/mongodb/admin.*")
files.each do |file|
  describe file("#{file}") do
    it { should be_mode 600 }
    it { should be_owned_by 'mongodb' }
    it { should be_grouped_into 'nogroup' }
  end
end

