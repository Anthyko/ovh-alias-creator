# OVH Redirect Creator

Small CLI tool to manage **OVH email redirections** from the command line.

It allows you to:

- create email redirect
- list existing redirects
- delete a redirect

The script automatically handles the **OVH consumer key authorization** the first time it runs.

---

## Requirements

- Python 3
- An OVH account
- An OVH API application key and secret

Install the Python dependency:

```bash
poetry install
```

---

## OVH API credentials

Create an application on the OVH API console, refer to [the official documentation](https://eu.api.ovh.com/createApp/) : 

https://eu.api.ovh.com/createApp/ => This is for eu

You will receive:

- `application_key`
- `application_secret`

Create the file `ovh.conf` at the root of the project:

```ini
[default]
endpoint=ovh-eu
application_key=YOUR_APP_KEY
application_secret=YOUR_APP_SECRET
```

The script will automatically generate and store the **consumer_key** during the first run.

---

## Usage

`ovh-redirect` is defined as a poetry script, use it to interact with the application

### List redirects

```bash
ovh-redirect example.com list
```

### Create a redirect

```bash
ovh-redirect example.com create contact@example.com me@gmail.com
```

### Delete a redirect

```bash
ovh-redirect example.com delete 897234892738...
```


---

## First run

When the script runs for the first time, it will:

1. request a **consumer key**
2. display an **authorization URL**
3. ask you to open the URL and authorize the application
4. save the `consumer_key` in `ovh.conf`

After that, the script should work without additional setup.

---

## Example output

```
id: 24823423423 - contact@example.com -> me@gmail.com
id: 32489672348 - support@example.com -> helpdesk@gmail.com
```

---

## License

MIT
