from twilio.rest import Client

from verifications.constants import body


account_sid = "AC34ca032e88eba6f61fec2bd095bf9553"
auth_token = "4cb7682d3ffca0621ea9a5c768af1294"

# client = Client(account_sid,auth_token)
#
# def send_sms(user_code,phone_number):
#     message = client.messages.create(
#         body=f'Hi, Your user and verification code is {user_code}!',
#         from_="+19093233096",
#         to=f'{phone_number}'
#     )
#     print(message.sid)


# Create single instace
class Twilio(object):
    def __new__(cls, *args, **kwargs):
        """
        Define single instance initialize method
        :return: single instance
        """
        # Check whether instance is exist, is not, create instance and return it
        # if yse, return
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.client = Client(account_sid,auth_token)
        return cls._instance

    # def send_sms(self, user_code, phone_number, time_limit):
    #     """ Single instance method of sending SMS verify code"""
    #     message = self.client.messages.create(
    #         body=f'Hi, Your user and verification code is {user_code}! Please enter correctly within {time_limit} minutes',
    #         from_="+19093233096",
    #         to=f'{phone_number}'
    #     )
    #     print(message.sid)
    def send_sms(self, user_code, time_limit, phone_number, tempID):
        """ Single instance method of sending SMS verify code"""
        message = self.client.messages.create(
            body=body(user_code, time_limit, tempID),
            from_="+19093233096",
            # status_callback='http://postb.in/1234abcd',
            to=f'{phone_number}'
        )
        print(message.sid)
        if message.error_code is None:
            return 0
        else:
            return -1


if __name__ == '__main__':
    Twilio().send_sms('123456', 5, '+14088169843', 1)