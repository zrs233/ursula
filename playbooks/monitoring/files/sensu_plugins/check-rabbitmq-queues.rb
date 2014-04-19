#!/usr/bin/env ruby
#
# Check Rabbitmq Queues
# ===
#
# Purpose: to check the size or number of rabbitmq queues.
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

require 'rubygems' if RUBY_VERSION < '1.9.0'
require 'sensu-plugin/check/cli'

class CheckRabbitCluster < Sensu::Plugin::Check::CLI
  option  :warning,
          :description => "Minimum number of messages in the queue before alerting warning",
          :short => '-w NUMBER',
          :long => '--warn NUMBER'

  option  :critical,
          :description => "Minimum number of messages in the queue before alerting critical",
          :short => '-c NUMBER',
          :long => '--crit NUMBER'

  option  :ignore,
          :description => "Comma-separated list of queues to ignore in our check",
          :short => '-i QUEUE,QUEUE,...',
          :long => '--ignore QUEUE,QUEUE,...',
          :default => nil

  option  :type,
          :description => "Type of check to perform",
          :short => '-t TYPE',
          :long => '--type TYPE',
          :valid => %w[length number],
          :default => 'length'

  def set_defaults
    if config[:type] == 'length'
      config[:warning] = 5 unless !config[:warning].nil?
      config[:critical] = 20 unless !config[:critical].nil?
    else
      config[:warning] = 200 unless !config[:warning].nil?
      config[:critical] = 400 unless !config[:critical].nil?
    end
  end

  def run

    set_defaults

    ignored_queues = []
    ignored_queues = config[:ignore].split(',') unless config[:ignore] == nil

    ignored = ""
    ignored = "| grep -v " unless ignored_queues == []
    ignored_queues.each do |queue|
      ignored += "-e #{queue} "
    end

    suffix = "awk '{sum += $2} END {print sum}'"
    if config[:type] == 'number'
      suffix = "wc -l"
    end

    cmd = "/usr/bin/timeout -s 9 1s /usr/sbin/rabbitmqctl list_queues -p / #{ignored}| #{suffix}"
    count = `#{cmd}`

    # Rabbit failure checking
    if $?.exitstatus == 137
      critical "Listing queues is timing out"
    elsif $?.exitstatus > 0
      critical "Error checking rabbit queues"
    end

    # Queue size checking
    queue_count = count.to_i
    if queue_count > 0
      if queue_count > config[:critical].to_i
        critical "CRITICAL: Queues not empty: #{queue_count}"
      elsif queue_count > config[:warning].to_i
        warning "WARNING: Queues not empty: #{queue_count}"
      end
    end
    ok
  end
end
