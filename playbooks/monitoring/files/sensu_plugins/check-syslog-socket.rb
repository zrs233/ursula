#!/usr/bin/env ruby
#
# Check Syslog Socket Plugin
# ===
#
# This plugin checks that the local syslog socket is accepting messages
# without blocking.
#
# Copyright 2014 Dustin Lundquist <dlundquist@bluebox.net>
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

require 'rubygems' if RUBY_VERSION < '1.9.0'
require 'sensu-plugin/check/cli'
require 'timeout'
require 'socket'

class CheckSyslogSocket < Sensu::Plugin::Check::CLI

  option :log_socket,
         :description => "Path to log socket",
         :short => '-s SOCKET',
         :long => '--log-socket SOCKET',
         :default => '/dev/log'

  option :warn,
         :short => '-w WARN',
         :proc => proc {|a| a.to_f },
         :default => 200

  option :crit,
         :short => '-c CRIT',
         :proc => proc {|a| a.to_f },
         :default => 1000


  class WarningExceeded < StandardError
  end

  class CriticalExceeded < StandardError
  end

  def run
    Timeout::timeout(config[:crit] * 1e-3, CriticalExceeded) do
      Timeout::timeout(config[:warn] * 1e-3, WarningExceeded) do
        do_syslog_msg
      end
    end

    ok "#{config[:log_socket]} accepted message"
  rescue WarningExceeded
    warning "#{config[:log_socket]} took longer than #{config[:warn]}ms to accept message"
  rescue CriticalExceeded
    critical "#{config[:log_socket]} took longer than #{config[:crit]}ms to accept message"
  end

  private

  def log_msg
    facility = 23   # Local 7
    level = 7       # Debug
    priority = facility * 8 + level
    timestamp = Time.now.strftime("%c")
    hostname = Socket.gethostname

    "<#{priority}>#{timestamp} check-syslog-socket: ping"
  end

  def do_syslog_msg
    log_socket_address = Socket.pack_sockaddr_un(config[:log_socket])

    socket = Socket::new(Socket::AF_UNIX, Socket::SOCK_DGRAM, 0)
    socket.send(log_msg, 0, log_socket_address)
    socket.close
  end
end
