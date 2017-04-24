import logging
import os
import nest
import time


class MyNest(nest.Nest):

    def __init__(self, dummy_mode=False):
        self._dummy_data = {}
        self.logger = logging.getLogger('nest_wrapper')
        logging.basicConfig()
        kwargs = self._get_auth_kwargs()

        super(MyNest, self).__init__(**kwargs)
        self._check_authorization()
        self.thermostat = self._get_thermostat()
        if dummy_mode:
            self.thermostat._set = self._dummy_set
        print "Using thermostat: {}".format(self.thermostat.name)

    def _get_auth_kwargs(self):
        kwargs = {
            'client_id': os.environ['NEST_PRODUCT_ID'],
            'client_secret': os.environ['NEST_PRODUCT_SECRET'],
            'access_token_cache_file': 'nest.json',
        }
        return kwargs

    def _dummy_set(self, what, data):
        self._dummy_data[what] = data

    def _check_authorization(self):
        if self.authorization_required:
            self.logger.info("Authorization required.")
            print('Go to ' + self.authorize_url + ' to authorize, then enter PIN below')
            pin = raw_input("PIN: ")
            self.request_token(pin)

    def _get_thermostat(self):
        thermos = self.thermostats
        if len(thermos) != 1:
            raise Exception("Found {} thermostats, expected only 1".format(len(thermos)))
        return thermos[0]

    def _validate_temp(self, temp):
        assert isinstance(temp, (int, float)) and temp in range(55, 85), "Invalid temp: {}".format(temp)

    def _set_mode(self, mode):
        self.logger.debug("Setting mode to '{}'".format(mode))
        self.thermostat.mode = mode

    def set_to_heat(self):
        self._set_mode('heat')

    def set_to_cool(self):
        self._set_mode('cool')

    @property
    def current_temp(self):
        return self.thermostat.temperature

    def set_target_temp(self, target_temp):
        self._validate_temp(target_temp)
        curr_temp = self.thermostat.temperature
        if target_temp == self.thermostat.target:
            return

        if target_temp > curr_temp:
            self.set_to_heat()
        else:
            self.set_to_cool()

        self.logger.debug("Setting target temp to {}*F".format(target_temp))
        self.thermostat.target = target_temp


if __name__  == "__main__":
    mynest = MyNest(dummy_mode=True)
    mynest.logger.setLevel(logging.DEBUG)
    print "Current temp: {}*F".format(mynest.current_temp)
    mynest.set_target_temp(70)
    time.sleep(5)
    mynest.set_target_temp(80)
    time.sleep(5)
    mynest.set_target_temp(mynest.current_temp)