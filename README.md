# annotation-tools: Streamlit annotation app

Intended to be the base for a Streamlit app that could be used for annotation, but also now using it for experimentation with the LLM hub.

We would probably rename the repo before making it public.

Nothing is expected to be fully stable in this repository.


## Development

Primary contributor:

 - Zachary Levonian (<levon003@umn.edu>)

## Local development setup

This project uses `make` and `Poetry` to manage and install dependencies.

On Windows, you'll need to use WSL and maybe make some other changes.

### Python development

Use `make install` to install all needed dependencies (including the pre-commit hooks and Poetry).

You'll probably need to manually add Poetry to your PATH, e.g. by updating your `.bashrc` (or relevant equivalent):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Run tests

```bash
make test
```

### Run Jupyter Lab

```bash
make jupyter
```

Which really just runs `poetry run jupyter lab`, so feel free to customize your Jupyter experience.

### Other useful commands

 - `poetry run <command>` - Run the given command, e.g. `poetry run pytest` invokes the tests.
 - `poetry add <package>` - Add the given package as a dependency. Use flag `-G dev` to add it as a development dependency.

### Streamlit

A few notes about the Streamlit app.

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
