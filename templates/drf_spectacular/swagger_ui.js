"use strict";

const swaggerSettings = {{ settings|safe }};
const schemaAuthNames = {{ schema_auth_names|safe }};
let schemaAuthFailed = false;
const plugins = [];

const reloadSchemaOnAuthChange = () => {
  return {
    statePlugins: {
      auth: {
        wrapActions: {
          authorizeOauth2:(ori) => (...args) => {
            schemaAuthFailed = false;
            setTimeout(() => ui.specActions.download());
            return ori(...args);
          },
          authorize: (ori) => (...args) => {
            schemaAuthFailed = false;
            setTimeout(() => ui.specActions.download());
            return ori(...args);
          },
          logout: (ori) => (...args) => {
            schemaAuthFailed = false;
            setTimeout(() => ui.specActions.download());
            return ori(...args);
          },
        },
      },
    },
  };
};

if (schemaAuthNames.length > 0) {
  plugins.push(reloadSchemaOnAuthChange);
}

const uiInitialized = () => {
  try {
    ui;
    return true;
  } catch {
    return false;
  }
};

const isSchemaUrl = (url) => {
  if (!uiInitialized()) {
    return false;
  }
  return url === new URL(ui.getConfigs().url, document.baseURI).href;
};

const isTokenUrl = (url) => {
  try {
    const u = new URL(url, document.baseURI);
    return u.pathname.endsWith("/api/auth/token/");
  } catch {
    return false;
  }
};

const setStatus = (text, kind = "info") => {
  const el = document.getElementById("quick-auth-status");
  if (!el) return;
  el.textContent = text || "";
  if (kind === "ok") el.style.color = "#99f6e4";
  else if (kind === "bad") el.style.color = "#fbcfe8";
  else el.style.color = "var(--text-muted)";
};

const getSpecJson = () => {
  if (!uiInitialized()) return null;
  try {
    const spec = ui.getState().get("spec");
    if (!spec) return null;
    const json = spec.get("json");
    if (!json) return null;
    return json.toJS ? json.toJS() : json;
  } catch {
    return null;
  }
};

const detectBearerAuthName = () => {
  if (Array.isArray(schemaAuthNames) && schemaAuthNames.length > 0) {
    return schemaAuthNames[0];
  }
  const spec = getSpecJson();
  const schemes = spec?.components?.securitySchemes;
  if (!schemes) return null;
  for (const [name, def] of Object.entries(schemes)) {
    if (def?.type === "http" && def?.scheme === "bearer") return name;
  }
  return null;
};

const authorizeWithAccess = (accessToken) => {
  if (!accessToken) return false;
  if (!uiInitialized()) return false;
  const authName = detectBearerAuthName();
  if (!authName) return false;
  const payload = {};
  payload[authName] = { schema: { type: "http", scheme: "bearer" }, value: accessToken };

  try {
    ui.authActions.authorize(payload);
    localStorage.authorized = JSON.stringify(payload);
    return true;
  } catch (e) {
    console.error("authorize failed", e);
    return false;
  }
};

const responseInterceptor = async (response, ...args) => {
  if (!response.ok && isSchemaUrl(response.url)) {
    console.warn("schema request received '" + response.status + "'. disabling credentials for schema till logout.");
    if (!schemaAuthFailed) {
      schemaAuthFailed = true;
      setTimeout(() => ui.specActions.download());
    }
    return response;
  }

  // Если пользователь получил JWT через Swagger "Execute", включаем авторизацию автоматически.
  if (response.ok && isTokenUrl(response.url)) {
    try {
      const clone = response.clone();
      const data = await clone.json();
      if (data && data.access) {
        const ok = authorizeWithAccess(data.access);
        if (ok) {
          setStatus("Готово: доступ включён. Теперь можно выполнять любые запросы ниже.", "ok");
        }
      }
    } catch (e) {
      // ignore
    }
  }
  return response;
};

const injectAuthCredentials = (request) => {
  let authorized;
  if (uiInitialized()) {
    const state = ui.getState().get("auth").get("authorized");
    if (state !== undefined && Object.keys(state.toJS()).length !== 0) {
      authorized = state.toJS();
    }
  } else if (![undefined, "{}"].includes(localStorage.authorized)) {
    authorized = JSON.parse(localStorage.authorized);
  }
  if (authorized === undefined) {
    return;
  }
  const names = (Array.isArray(schemaAuthNames) && schemaAuthNames.length > 0)
    ? schemaAuthNames
    : Object.keys(authorized || {});

  for (const authName of names) {
    const authDef = authorized?.[authName];
    if (authDef === undefined || authDef.schema === undefined) {
      continue;
    }
    if (authDef.schema.type === "http" && authDef.schema.scheme === "bearer") {
      request.headers["Authorization"] = "Bearer " + authDef.value;
      return;
    } else if (authDef.schema.type === "http" && authDef.schema.scheme === "basic") {
      request.headers["Authorization"] = "Basic " + btoa(authDef.value.username + ":" + authDef.value.password);
      return;
    } else if (authDef.schema.type === "apiKey" && authDef.schema.in === "header") {
      request.headers[authDef.schema.name] = authDef.value;
      return;
    } else if (authDef.schema.type === "oauth2" && authDef.token.token_type === "Bearer") {
      request.headers["Authorization"] = `Bearer ${authDef.token.access_token}`;
      return;
    }
  }
};

const requestInterceptor = (request, ...args) => {
  if (request.loadSpec && !schemaAuthFailed) {
    try {
      injectAuthCredentials(request);
    } catch (e) {
      console.error("schema auth injection failed with error: ", e);
    }
  }
  if (!["GET", undefined].includes(request.method) && request.credentials === "same-origin") {
    request.headers["{{ csrf_header_name }}"] = "{{ csrf_token }}";
  }
  return request;
};

const ui = SwaggerUIBundle({
  url: "{{ schema_url|escapejs }}",
  dom_id: "#swagger-ui",
  presets: [SwaggerUIBundle.presets.apis],
  plugins,
  layout: "BaseLayout",
  requestInterceptor,
  responseInterceptor,
  ...swaggerSettings,
});

{% if oauth2_config %}ui.initOAuth({{ oauth2_config|safe }});{% endif %}

// Быстрый вход сверху страницы: логин/пароль → получить токен → автоматически включить доступ.
window.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("quick-auth-form");
  const clearBtn = document.getElementById("quick-auth-clear");
  const uEl = document.getElementById("quick-auth-username");
  const pEl = document.getElementById("quick-auth-password");

  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (uEl) uEl.value = "";
      if (pEl) pEl.value = "";
      setStatus("Сброшено.", "info");
      try {
        localStorage.authorized = "{}";
        if (uiInitialized()) ui.authActions.logout();
      } catch {}
    });
  }

  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = (uEl && uEl.value || "").trim();
    const password = (pEl && pEl.value || "").trim();
    if (!username || !password) {
      setStatus("Введите логин и пароль.", "bad");
      return;
    }
    setStatus("Входим…", "info");
    try {
      const res = await fetch("/api/auth/token/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "accept": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "same-origin",
      });
      if (!res.ok) {
        setStatus("Не удалось войти. Проверьте логин/пароль.", "bad");
        return;
      }
      const data = await res.json();
      if (data && data.access) {
        const ok = authorizeWithAccess(data.access);
        if (ok) {
          setStatus("Готово: доступ включён. Теперь можно выполнять запросы ниже.", "ok");
        } else {
          setStatus("Токен получен, но не удалось включить доступ автоматически.", "bad");
        }
      } else {
        setStatus("Ответ без access-токена. Попробуйте ещё раз.", "bad");
      }
    } catch (err) {
      console.error(err);
      setStatus("Ошибка сети. Попробуйте ещё раз.", "bad");
    }
  });
});

