import argparse
import configparser

import ovh

CONFIG_PATH = "ovh.conf"
CONFIG_SECTION = "default"


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f)


def get_setting(config, key):
    try:
        return config[CONFIG_SECTION][key]
    except KeyError:
        raise SystemExit(f"Missing '{key}' in {CONFIG_PATH}")


def get_client(config, consumer_key=None):
    return ovh.Client(
        endpoint=get_setting(config, "endpoint"),
        application_key=get_setting(config, "application_key"),
        application_secret=get_setting(config, "application_secret"),
        consumer_key=consumer_key,
    )


def ensure_consumer_key(config, domain):
    consumer_key = config.get(CONFIG_SECTION, "consumer_key", fallback=None)
    if consumer_key:
        return consumer_key

    client = get_client(config)

    request = client.new_consumer_key_request()
    request.add_rules(ovh.API_READ_WRITE, f"/email/domain/{domain}/redirection")
    request.add_rules(ovh.API_READ_WRITE, f"/email/domain/{domain}/redirection/*")

    result = request.request()

    print("Open this URL and authorize the application:")
    print(result["validationUrl"])
    input("Press Enter after authorization... ")

    config[CONFIG_SECTION]["consumer_key"] = result["consumerKey"]
    save_config(config)

    return result["consumerKey"]


def create_redirect(domain, alias, destination):
    config = load_config()
    consumer_key = ensure_consumer_key(config, domain)
    client = get_client(config, consumer_key)

    client.post(
        f"/email/domain/{domain}/redirection",
        _from=alias,
        to=destination,
        localCopy=False,
    )

    print(f"Redirect created: {alias} -> {destination}")


def list_redirects(domain):
    config = load_config()
    consumer_key = ensure_consumer_key(config, domain)
    client = get_client(config, consumer_key)

    redirect_ids = client.get(f"/email/domain/{domain}/redirection")

    if not redirect_ids:
        print("No redirects found")
        return

    for redirect_id in redirect_ids:
        redirect = client.get(f"/email/domain/{domain}/redirection/{redirect_id}")
        print(f" id: {redirect['id']} - {redirect['from']} -> {redirect['to']}")


def delete_redirect(domain, redirect_id):
    config = load_config()
    consumer_key = ensure_consumer_key(config, domain)
    client = get_client(config, consumer_key)

    client.delete(f"/email/domain/{domain}/redirection/{redirect_id}")

    print(f"Redirect deleted (id: {redirect_id})")


def main():
    parser = argparse.ArgumentParser(description="OVH email redirect manager")
    parser.add_argument("domain", help="Domain name, e.g. example.com")

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a redirect")
    create_parser.add_argument("alias", help="Source email address")
    create_parser.add_argument("destination", help="Destination email address")

    subparsers.add_parser("list", help="List redirects")

    delete_parser = subparsers.add_parser("delete", help="Delete a redirect")
    delete_parser.add_argument("id", help="Redirect ID")

    args = parser.parse_args()

    if args.command == "create":
        create_redirect(args.domain, args.alias, args.destination)
    elif args.command == "list":
        list_redirects(args.domain)
    elif args.command == "delete":
        delete_redirect(args.domain, args.id)


if __name__ == "__main__":
    main()
