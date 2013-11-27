#!/usr/bin/env ruby
#
# Check Rabbitmq Queues
# ===
#
# Purpose: to check the size of the rabbitmq queues.
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

require 'rubygems' if RUBY_VERSION < '1.9.0'
require 'sensu-plugin/check/cli'

class CheckRabbitCluster < Sensu::Plugin::Check::CLI
  option  :expected,
          :description => "Minimum number of messages in the queue before alerting",
          :short => '-m NUMBER',
          :long => '--min NUMBER',
          :default => 5

  def run
    cmd = "/usr/bin/timeout -s 9 1s /usr/sbin/rabbitmqctl list_queues -p / | awk '{sum += $2} END {print sum}'"
    count = `#{cmd}`

    # Rabbit failure checking
    if $?.exitstatus == 137
      critical "Listing queues is timing out"
    elsif $?.exitstatus > 0
      critical "Error checking rabbit queues"
    end

    # Queue size checking
    if count.to_i > 0
      if count.to_i > config[:min].to_i
        critical "Queues not empty: #{count}"
      end
    else
      ok
    end
  end
end
