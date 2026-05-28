# Guia didatico: validar JWT nos servicos consumidores (sem JWKS)

Este guia mostra a forma mais simples de integrar os servicos:

1. Auth assina o token com `JWT_PRIVATE_KEY_PEM`
2. cada servico consumidor valida localmente com `JWT_PUBLIC_KEY_PEM`

## 1) Configuracao em cada servico consumidor

Cada servico precisa ter no `.env`:

```env
JWT_ISSUER="https://auth.local"
JWT_AUDIENCE="internal-apis"
JWT_PUBLIC_KEY_PEM="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
```

Importante:

- o `JWT_PUBLIC_KEY_PEM` deve ser exatamente a chave publica do Auth
- mantenha os `\n` literais no `.env`

## 2) O que validar

Para toda rota protegida:

1. ler `Authorization`
2. extrair `Bearer <token>`
3. validar assinatura RS256 com `JWT_PUBLIC_KEY_PEM`
4. validar `iss`, `aud` e `exp`
5. validar se `sub` existe
6. montar `request.auth = { id: sub, token }`

Se algo falhar, retornar `401`.

## 3) Exemplo pratico (Node/Express + jose)

```ts
import express from "express";
import { importSPKI, jwtVerify } from "jose";

const app = express();

const ISSUER = process.env.JWT_ISSUER!;
const AUDIENCE = process.env.JWT_AUDIENCE!;
const PUBLIC_KEY_PEM = process.env.JWT_PUBLIC_KEY_PEM!.replace(/\\n/g, "\n");

let publicKeyPromise: ReturnType<typeof importSPKI> | null = null;

function getPublicKey() {
  if (!publicKeyPromise) {
    publicKeyPromise = importSPKI(PUBLIC_KEY_PEM, "RS256");
  }

  return publicKeyPromise;
}

function authMiddleware() {
  return async (req, res, next) => {
    try {
      const authHeader = req.header("authorization");

      if (!authHeader) {
        return res
          .status(401)
          .json({ message: "Missing Authorization header" });
      }

      const [scheme, token] = authHeader.split(" ");

      if (!scheme || !token || scheme.toLowerCase() !== "bearer") {
        return res
          .status(401)
          .json({ message: "Authorization must be Bearer token" });
      }

      const publicKey = await getPublicKey();

      const { payload } = await jwtVerify(token, publicKey, {
        issuer: ISSUER,
        audience: AUDIENCE,
        algorithms: ["RS256"],
      });

      if (typeof payload.sub !== "string" || !payload.sub.trim()) {
        return res.status(401).json({ message: "Invalid token claims" });
      }

      req.auth = {
        id: payload.sub,
        token,
      };

      return next();
    } catch {
      return res
        .status(401)
        .json({ message: "Invalid or expired access token" });
    }
  };
}

app.get("/profile/me", authMiddleware(), (req, res) => {
  return res.json({ userId: req.auth.id });
});
```

## 4) Propagacao entre servicos (A -> B)

Quando API A chamar API B em nome do usuario:

- repasse o mesmo `Authorization: Bearer <token>`
- API B valida esse token com `JWT_PUBLIC_KEY_PEM`
- API B usa `sub` como identidade confiavel

```ts
const authHeader = req.header("authorization");

const response = await fetch("http://courses-service/courses/me", {
  headers: { Authorization: authHeader! },
});
```

## 5) Checklist rapido

- todos os servicos com o mesmo `JWT_PUBLIC_KEY_PEM`
- middleware valida assinatura + `iss` + `aud` + `exp`
- `sub` obrigatorio
- retorna `401` para token ausente/invalido/expirado
- usa `sub` como ID confiavel

## 6) Trade-off dessa abordagem

Vantagem:

- muito simples para implementar e explicar

Desvantagem:

- quando trocar a chave publica, precisa atualizar o `.env` de todos os servicos consumidores
