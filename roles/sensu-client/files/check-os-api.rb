#!/usr/bin/env ruby
#
# Check OS API
# ===
#
# Purpose: to manage a request to an openstack service api endpoint.
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

require 'rubygems' if RUBY_VERSION < '1.9.0'
require 'sensu-plugin/check/cli'
require 'net/http'
require 'net/https'
require 'json'

class CheckOSApi < Sensu::Plugin::Check::CLI

  # path to openstack rc file.
  # expected stackrc format: http://docs.openstack.org/trunk/install-guide/install/yum/content/novarc-file.html
  option :stackrc, :long  => '--stackrc STACKRC_PATH'

  # service endpoint opts
  option :host, :long => '--host FQDN or IP'
  option :port, :long => '--port PORT'
  option :path, :long => '--path PATH'
  option :match_str, :long => '--match-str STRING'
  option :use_ssl, :long => '--use-ssl BOOLEAN'

  def run
    @http_timeout = 15

    stackrc = File.new(config[:stackrc], "r")
    stackrc.each_line do |line|
      case
      when line.match("OS_USERNAME")
        @auth_user = line[/.+OS_USERNAME=(.*)/, 1]
      when line.match("OS_PASSWORD")
        @auth_password = line[/.+OS_PASSWORD=(.*)/, 1]
      when line.match("OS_AUTH_URL")
        @auth_host = line[/.+OS_AUTH_URL=http.:\/\/(.*)\:.*/, 1]
        @auth_path = "/" + line[/.+OS_AUTH_URL=http.:\/\/.*\:\d+\/(.*)/, 1] + "/tokens"
        @auth_port = line[/.+OS_AUTH_URL=http.:\/\/.*\:(\d+)\//, 1]
      when line.match("OS_TENANT_NAME")
        @tenant_name = line[/.+OS_TENANT_NAME=(.*)/, 1]
      end
    end
    stackrc.close

    get_auth_token
    check_api_path
  end

  def check_api_path
    http = Net::HTTP.new(config[:host], config[:port])
    req = Net::HTTP::Get.new(config[:path])
    req["X-Auth-Token"] = @auth_token
    res = http.request(req)

    if res.body.empty? || JSON.parse(res.body)[config[:match_str]].nil?
      critical "no results from API at: #{config[:host]}, #{config[:port]} #{config[:path]}"
    else
      ok
    end
  end

  # obtain auth-token from Keystone API
  def get_auth_token
    payload = {
      "auth" => {
        "passwordCredentials" => {
          "username" => @auth_user,
          "password" => @auth_password
        },
        "tenantName" => @tenant_name
       }
    }.to_json

    # Throw Timeout::Error exception if HTTP req/res
    # runs longer than @http_timeout.
    begin
      timeout(@http_timeout) do
        http = Net::HTTP.new(@auth_host, @auth_port)
        if config[:use_ssl] && config[:use_ssl].match(/true/i)
          http.use_ssl = true
        end
        req = Net::HTTP::Post.new(@auth_path)
        req.body = payload
        req["Content-type"] = "application/json"
        res = http.request(req)
        @auth_token = JSON.parse(res.body)["access"]["token"]["id"]
        if @auth_token.empty?
          abort "could not retrieve token from keystone"
        end
      end
    rescue Timeout::Error
      puts "Connection timed out"
    rescue => e
      puts "Connection error: #{e.message}"
    end

    return @auth_token
  end
end
