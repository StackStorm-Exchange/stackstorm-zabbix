require 'zbxapi'
require 'spec_helper'

ZABBIX_USER = ENV['ZABBIX_USER'] || 'admin'
ZABBIX_SENDTO = ENV['ZABBIX_SENDTO'] || 'admin'
ZABBIX_PASSWORD = ENV['ZABBIX_PASSWORD'] || 'zabbix'
ZABBIX_API_ENDPOINT = ENV['ZABBIX_API'] || 'http://localhost/'
ZABBIX_DISPATCHER_MEDIA_TYPE = ENV['ZABBIX_DISPATCHER_MEDIA_TYPE'] || 'script'

describe 'Tests for registering Zabbix for StackStorm' do
  before(:all) do
    @client = ZabbixAPI.new(ZABBIX_API_ENDPOINT)

    expect(try_to_login).not_to be_a(RuntimeError)
  end

  # run script to register configurations for StackStorm to the Zabbix
  describe command("tools/register_st2_config_to_zabbix.py " \
                   "-u #{ ZABBIX_USER } " \
                   "-s #{ ZABBIX_SENDTO } " \
                   "-p #{ ZABBIX_PASSWORD } " \
                   "-z #{ ZABBIX_API_ENDPOINT } " \
                   "-t #{ ZABBIX_DISPATCHER_MEDIA_TYPE }") do
    its(:exit_status) { should eq 0 }
    its(:stdout) do 
      should match /^Success to register the configurations for StackStorm to the Zabbix Server./
    end

    describe 'Check each configurations are actually set in the Zabbix' do
      it 'MediaType configuration is set' do
        expect(@client.mediatype.get.find {|x| x['description'] == 'StackStorm'}).to_not be_nil
      end

      it 'Action configuration is set' do
        expect(@client.action.get.find { |x| x['name'].include?('StackStorm')}).to_not be_nil
      end
    end
  end

  # This method wait to start and initialize Zabbix-server and Zabbix-Web
  def try_to_login(retry_count = 0)
    begin
      return @client.login(ZABBIX_USER, ZABBIX_PASSWORD)
    rescue => e
      if retry_count < 60
        # make a delay before retrying
        sleep 1
        return try_to_login(retry_count + 1)
      else
        return e
      end
    end
  end
end
