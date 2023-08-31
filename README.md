# annotation-tools: Streamlit annotation app backed by Supabase


## Development

Primary contributor:

 - Zachary Levonian (<levon003@umn.edu>)

## Local development setup

This project uses `make` and `Poetry` to manage and install dependencies

### Python development

Use `make install` to install all needed dependencies (including the pre-commit hooks).

### Run tests

```bash
make test
```

### Other useful commands

 - `poetry run <command>` - Run the given command, e.g. `poetry run pytest` invokes the tests.
 - `poetry add <package>` - Add the given package as a dependency. Use flag `-G dev` to add it as a development dependency.

### Streamlit

A few notes about the app.

#### Authentication

For local development, streamlit secrets need to be stored in `.streamlit/secrets.toml`

Here's a sample file:
```
AUTH_TOKEN = "argon2:$argon2id$v=19$m=10240,t=10,p=8$MuVIOw20jkOi1nKR90hPhA$H22nY8aNyfztLYQCSj5NRw5/Cy2WOo6kl3K61RyaoZY"
PASSWORD = "argon2:$argon2id$v=19$m=10240,t=10,p=8$MuVIOw20jkOi1nKR90hPhA$H22nY8aNyfztLYQCSj5NRw5/Cy2WOo6kl3K61RyaoZY"
```

To generate the auth_token:
```
>>> import notebook.auth.security
>>> notebook.auth.security.passwd()
Enter password: abc
Verify password: abc
'argon2:$argon2id$v=19$m=10240,t=10,p=8$MuVIOw20jkOi1nKR90hPhA$H22nY8aNyfztLYQCSj5NRw5/Cy2WOo6kl3K61RyaoZY'
```

If the AUTH_TOKEN is provided in the secrets, can authenticate automatically via URL parameter, e.g. `{base_url}?auth_token=abc`.
