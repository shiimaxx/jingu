# jingu

My hobby project of creating a jinja2-like template engine with Python.


## Implemented

### Variables

```
{{ foo }}
{{ foo.bar }}
{{ foo['bar'] }}
```

### Calculates

```
{{ 1 + 1 }}
{{ 3 - 2 }}
{{ 1 / 2 }}
{{ 20 // 7 }}
{{ 11 % 7 }}
{{ 2 * 2 }}
```

### If statement

```
{% if True %}True!{% endif %}
{% if False %}False!{% endif %}
```

## TODO

- `elif`, `else`
- `for`
