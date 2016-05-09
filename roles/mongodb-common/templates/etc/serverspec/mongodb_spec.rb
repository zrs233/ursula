require 'spec_helper'

describe  file('/etc/mongod.conf') do
  it { should be_mode 640 }                    #MON001
  it { should be_owned_by 'root' }             #MON002
  it { should be_grouped_into 'mongodb' }      #MON003
  it { should contain 'logappend=true' }       #MON004
  it { should contain 'logpath=/var/log/mongodb/mongod.log' } #MON005
end

describe file ('/var/lib/mongodb') do    
  it { should be_directory }              #MON006
  it { should be_mode 755 }               #MON008
  it { should be_owned_by 'mongodb' }     #MON007
  it { should be_grouped_into 'mongodb'}  #MON009
end

files = Dir.glob("/var/lib/mongodb/local.*")
files.each do |file|
  describe file("#{file}") do
    it { should be_mode 600 }               #MON010
    it { should be_owned_by 'mongodb' }     #MON011
    it { should be_grouped_into 'nogroup' } #MON012
  end
end

files = Dir.glob("/var/lib/mongodb/admin.*")
files.each do |file|
  describe file("#{file}") do
    it { should be_mode 600 }               #MON010
    it { should be_owned_by 'mongodb' }     #MON011
    it { should be_grouped_into 'nogroup' } #MON012
  end
end

describe file ('/var/lib/mongodb/storage.bson') do
  it { should be_mode 644 }                 #MON013
  it { should be_owned_by 'mongodb' }       #MON014
  it { should be_grouped_into 'nogroup' }   #MON015
end

describe file ('/var/lib/mongodb/journal') do
  it { should be_directory }
  it { should be_mode 755 }                 #MON016
  it { should be_owned_by 'mongodb' }       #MON017
  it { should be_grouped_into 'nogroup' }   #MON018
end

files = Dir.glob("/var/lib/mongodb/journal/*")
files.each do |file|
  describe file("#{file}") do
    it { should be_mode 600 }               #MON019
    it { should be_owned_by 'mongodb' }     #MON020
    it { should be_grouped_into 'nogroup' } #MON021
  end
end

