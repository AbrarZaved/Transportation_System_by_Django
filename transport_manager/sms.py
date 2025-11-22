import os
import requests
import environ
from transportation_system.settings import BASE_DIR


def send_sms(driver_instance, route_instance, selected_time, bus_instance):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"ড্রাইভার {driver_instance.name}, আপনার বাস ডিউটি নির্ধারিত হয়েছে। রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। সময়মতো উপস্থিত থাকার অনুরোধ রইল।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": driver_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # raises exception for HTTP errors

        print("Status Code:", response.status_code)
        print("Response:", response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except Exception as err:
        print(f"An error occurred: {err}")


def send_helper_sms(helper_instance, route_instance, selected_time, bus_instance):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"হেলপার {helper_instance.name}, আপনার বাস ডিউটি নির্ধারিত হয়েছে। রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। সময়মতো উপস্থিত থাকার অনুরোধ রইল।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": helper_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()

        print("Helper SMS Status Code:", response.status_code)
        print("Helper SMS Response:", response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"Helper SMS HTTP error: {http_err}")

    except Exception as err:
        print(f"Helper SMS error: {err}")


def send_schedule_change_sms(
    driver_instance, route_instance, selected_time, bus_instance, changes
):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"ড্রাইভার {driver_instance.name}, আপনার বাস ডিউটি পরিবর্তন হয়েছে। {changes}। \n\n নতুন তথ্য - রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। সময়মতো উপস্থিত থাকার অনুরোধ রইল।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": driver_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Driver change SMS Status Code:", response.status_code)
        print("Driver change SMS Response:", response.text)
    except Exception as err:
        print(f"Driver change SMS error: {err}")


def send_schedule_cancellation_sms(
    driver_instance, route_instance, selected_time, bus_instance
):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"ড্রাইভার {driver_instance.name}, আপনার বাস ডিউটি বাতিল হয়েছে। রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। অনুগ্রহ করে অফিসে যোগাযোগ করুন।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": driver_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Driver cancellation SMS Status Code:", response.status_code)
        print("Driver cancellation SMS Response:", response.text)
    except Exception as err:
        print(f"Driver cancellation SMS error: {err}")


def send_helper_change_sms(
    helper_instance, route_instance, selected_time, bus_instance, changes
):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"হেলপার {helper_instance.name}, আপনার বাস ডিউটি পরিবর্তন হয়েছে। {changes}। \n\n নতুন তথ্য - রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। সময়মতো উপস্থিত থাকার অনুরোধ রইল।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": helper_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Helper change SMS Status Code:", response.status_code)
        print("Helper change SMS Response:", response.text)
    except Exception as err:
        print(f"Helper change SMS error: {err}")


def send_helper_cancellation_sms(
    helper_instance, route_instance, selected_time, bus_instance
):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"হেলপার {helper_instance.name}, আপনার বাস ডিউটি বাতিল হয়েছে। রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। অনুগ্রহ করে অফিসে যোগাযোগ করুন।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": helper_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Helper cancellation SMS Status Code:", response.status_code)
        print("Helper cancellation SMS Response:", response.text)
    except Exception as err:
        print(f"Helper cancellation SMS error: {err}")
