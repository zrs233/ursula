require 'spec_helper'
require 'socket'

describe user('rabbitmq') do
    it { should exist }
    it { should belong_to_group 'rabbitmq' }
end  

describe file('/etc/nova/nova.conf') do
  it { should_not contain /(rabbit_password=\w{0,7})$/ }
end

describe process("rabbitmq-server") do
  it { should be_running }
  its(:user) { should eq "rabbitmq" }
end

files = {'rabbitmq-env.conf'=> 600, 'enabled_plugins'=> 644}
files.each do |file , mode|
  describe file("/etc/rabbitmq/#{file}") do
    it { should be_file }
    it { should be_mode mode }
  end
end 

hostname = Socket.gethostname
files = ["rabbit@#{hostname}.log.1", "rabbit@#{hostname}-sasl.log", 'shutdown_err', 'shutdown_log', 'startup_err', 'startup_log']
files.each do |file|
  describe file("/var/log/rabbitmq/#{file}") do
    it { should be_file }
    it { should be_mode 644 }
  end
end 

describe file('/etc/logrotate.d/rabbitmq-server') do
  it { should exist }
  file_contents = [ '/var/log/rabbitmq/*.log {',
         '  weekly',
         '  missingok',
         '  rotate 20',
         '  compress',
         '  delaycompress',
         '  notifempty',
         '  sharedscripts',
         '  postrotate',
         '  /etc/init.d/rabbitmq-server rotate-logs > /dev/null',
         '}']
  file_contents.each do |file_line|
    it { should contain file_line }
  end
end

describe command('rabbitmqctl environment | grep default_user') do
  output = "      {default_user,<<\"guest\">>},\n      {default_user_tags,[administrator]},\n"
  its(:stdout) { should eq output }
end   

describe command('rabbitmqctl environment | grep log_levels') do
  output = "      {log_levels,[{connection,info}]},\n"
  its(:stdout) { should eq output }
end 

describe command('rabbitmqctl environment | grep log') do
  output = ["     [{error_logger,tty},\n",
            "      {error_logger,{file,\"/var/log/rabbitmq/rabbit@#{hostname}.log\"}},\n",
            "      {log_levels,[{connection,info}]},\n",
            "      {sasl_error_logger,\n",
            "          {file,\"/var/log/rabbitmq/rabbit@#{hostname}-sasl.log\"}},\n",
            "      {ssl_cert_login_from,distinguished_name},\n",
            "          [{backlog,128},\n",
            "     [{http_log_dir,none},\n {sasl,[{errlog_type,error},{sasl_error_logger,false}]},\n"].join()
  its(:stdout){ should eq output }
end         

