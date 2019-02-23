# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import random
import time
import sys
import iothub_client
from sense_hat import SenseHat
import datetime 
import json
# pylint: disable=E0611
from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 1000000

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0
SEND_SENSEHAT_CALLBACKS = 0

# Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
PROTOCOL = IoTHubTransportProvider.MQTT
VERBOSE = False

# read sense hat and send 
def read_and_send_measurements_from_sensehat(hubManager):
    global SEND_SENSEHAT_CALLBACKS    
    sense = SenseHat()    
    sense.clear()
    #Get temperature from the Humidity Sensor and convert to Farenheit     
    temperature = (sense.get_temperature() * 1.8) + 32
    #Get temperature from the Humidity Sensor and leave as Celsius    
    temperature_h = sense.get_temperature_from_humidity()    
    temperature_p = sense.get_temperature_from_pressure()
    #Get the Humidity 
    humidity = sense.get_humidity()
    #Get the Pressure in millibars and then convert to inches mercury       
    pressure = (sense.get_pressure()  * 29.92) / 1013.25   
    timeCreated = datetime.datetime.utcnow().isoformat()    
    MSG_TXT = "{\"temperatureF\": %.2f,\"temperatureC\": %.2f,\"pressureTemperature\": %.2f,\"humidity\": %.2f,\"pressure\": %.2f,\"timeCreated\": \"%s\"}"    
    msg_txt_formatted = MSG_TXT % (temperature, temperature_h, temperature_p, humidity, pressure, timeCreated)    
    message = IoTHubMessage(msg_txt_formatted)    
    SEND_SENSEHAT_CALLBACKS += 1
    print ( "The Current Temperature is: ", temperature, "F")
    print ( "Sending message ", SEND_SENSEHAT_CALLBACKS, " to upstream")
    print (message)
    hubManager.forward_event_to_output("output1", message, 0)
    

# Callback received when the message that we're forwarding is processed.
def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    print ( "Confirmation[",user_context,"] received for message with result =" , result) 
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: ", key_value_pair )
    SEND_CALLBACKS += 1
    print ( "    Total calls confirmed: ", SEND_CALLBACKS )


# receive_message_callback is invoked when an incoming message arrives on the specified 
# input queue (in the case of this sample, "input1").  Because this is a filter module, 
# we will forward this message onto the "output1" queue.
def receive_message_callback(message, hubManager):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "Data: <<<",message_buffer[:size].decode('utf-8'),">>> & Size=",size )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: ", key_value_pair )
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: ", RECEIVE_CALLBACKS )
    print ("Sending message to output2")
    hubManager.send_event_to_output("output2", message, 0)
    return IoTHubMessageDispositionResult.ACCEPTED


class HubManager(object):

    def __init__(
            self,
            messageTimeout,
            protocol,
            verbose):
        '''
        Communicate with the Edge Hub

        :param int messageTimeout: the maximum time in milliseconds until a message times out. The timeout period starts at IoTHubClient.send_event_async. By default, messages do not expire.
        :param IoTHubTransportProvider protocol: Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
        :param bool verbose: set to true to get detailed logs on messages
        '''
        self.messageTimeout = messageTimeout
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)
        self.client.set_option("messageTimeout", self.messageTimeout)
        self.client.set_option("product_info","SenseHatSensors Module")
        if verbose:
            self.client.set_option("logtrace", 1)#enables MQTT logging

    def send_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(outputQueueName, event, send_confirmation_callback, send_context)

    # Forwards the message received onto the next stage in the process.
    def forward_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(
            outputQueueName, event, send_confirmation_callback, send_context)

def main(protocol):
    try:
        print ( "\nPython \n", sys.version )
        print ( "IoT Edge Client for Python" )

        hub_manager = HubManager(MESSAGE_TIMEOUT,PROTOCOL,VERBOSE)

        print ( "Starting the Edge Python module using protocol ",hub_manager.client_protocol )
        print ( "The device is now waiting for messages ")

        while True:
            #Start sending environmental values
            read_and_send_measurements_from_sensehat(hub_manager)
            #wait for 30 seconds
            time.sleep(30)

    except IoTHubError as iothub_error:
        print ( "Unexpected error from IoTHub:",iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubModuleClient sample stopped" )

if __name__ == '__main__':
    main(PROTOCOL)