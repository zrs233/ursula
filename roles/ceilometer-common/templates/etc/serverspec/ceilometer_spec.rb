require 'spec_helper'

describe file('/etc/ceilometer/ceilometer.conf') do
  it { should contain('^admin_password[ ]*=[ ]*.\{8,\}') }
end

dirs = ['/etc/ceilometer/', '/var/log/ceilometer/']
dirs.each do |dir|
  describe file(dir) do
    it { should be_directory }
    it { should be_mode '755'}
  end
end

files = ['api_paste.ini', 'event_pipeline.yaml', 'policy.json',
  'ceilometer.conf', 'event_definitions.yaml', 'pipeline.yaml']
files.each do |file|
  describe file("/etc/ceilometer/#{file}") do
    it { should be_mode '644'}
  end
end

{% if inventory_hostname in groups['controller'] %}
processes = ['ceilometer-api',
  'ceilometer-collector',
  'ceilometer-agent-notification',
  'ceilometer-agent-central',
  'ceilometer-alarm-evaluator',
  'ceilometer-alarm-notifier']
processes.each do |process|
  describe process(process) do
    its(:user) { should eq 'ceilometer' }
  end
end
{% endif %}

files = Dir['/var/log/ceilometer/*']
files.each do |file|
  describe file(file) do
    it { should be_mode 644 }
  end
end

describe file("/etc/ceilometer/ceilometer.conf") do
  it { should contain '^debug = {{ ceilometer.logging.debug }}' }
end
