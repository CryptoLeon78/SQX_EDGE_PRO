# Guía: Sube SQX_EDGE_PRO a GitHub

**Workflow de confirmación-gated:** Cada paso requiere validación antes de avanzar.

---

## PASO 1: Prepara archivos de configuración

### 1.1 Actualiza `.gitignore`

Reemplaza el contenido de `SQX_EDGE_PRO\.gitignore` con el archivo `gitignore_improved` que tienes en outputs.

**En tu máquina:**
```bash
# Abre tu .gitignore actual
C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO\.gitignore

# Reemplaza TODO su contenido con gitignore_improved
```

**Validación:**
```bash
cd C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO
git add .gitignore
git status
# Debe mostrar solo .gitignore como changed
```

✅ **CONFIRMA**: ¿.gitignore actualizado sin errores? (Sí/No)

---

### 1.2 Actualiza `README.md`

Reemplaza `README.md` con el archivo `README_github` de outputs.

**En tu máquina:**
```bash
# Abre tu README.md actual
# Reemplaza TODO su contenido con README_github

# Guarda como README.md (no .txt, no _github)
```

**Validación:**
```bash
cd C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO

# Verifica estructura Markdown
# Abre en editor: debe tener # (H1), ## (H2), etc.
type README.md | head -20

# Commit
git add README.md
git status
```

✅ **CONFIRMA**: ¿README.md actualizado y validado? (Sí/No)

---

## PASO 2: Inicializa repositorio Git local

### 2.1 Si NO tienes `.git` aún

```bash
cd C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO

# Inicializa repo local
git init

# Configura usuario (usa mismo nombre/email que GitHub)
git config user.name "Tu Nombre"
git config user.email "tu.email@github.com"

# Verifica
git config --local user.name
git config --local user.email
```

**Validación:**
```bash
git log
# Si no hay commits aún, es normal
# Debe no mostrar error
```

✅ **CONFIRMA**: ¿Git inicializado con configuración correcta? (Sí/No)

---

### 2.2 Si YA tienes `.git`

```bash
cd C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO

# Verifica origen remoto actual
git remote -v

# Si apunta a otro servidor, resetea:
git remote remove origin
# Luego sigue sección "PASO 3"
```

✅ **CONFIRMA**: ¿Git local verificado? (Sí/No)

---

## PASO 3: Crea repositorio en GitHub

### 3.1 Login en GitHub

- Abre https://github.com
- Inicia sesión con tu cuenta
- Si no tienes cuenta, crea una en https://github.com/signup

### 3.2 Crea nuevo repositorio

1. Haz clic en **"+"** (arriba derecha) → **"New repository"**

2. **Completa formulario:**

| Campo | Valor |
|-------|-------|
| Repository name | `SQX_EDGE_PRO` (exacto) |
| Description | `Electron + FastAPI app for SQX portfolio management & MT5 data quality` |
| Visibility | Private (solo tú lo ves) o Public (todos lo ven) |
| Initialize repo | ❌ NO inicialices (ya tienes archivos) |

3. Haz clic en **"Create repository"**

### 3.3 Copia instrucciones

GitHub te mostrará:

```bash
git remote add origin https://github.com/tu-usuario/SQX_EDGE_PRO.git
git branch -M main
git push -u origin main
```

✅ **CONFIRMA**: ¿Repositorio creado en GitHub? (Sí/No)

---

## PASO 4: Vincula repositorio remoto

### 4.1 En tu máquina

```bash
cd C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO

# Añade remoto (reemplaza TU-USUARIO con tu nombre en GitHub)
git remote add origin https://github.com/TU-USUARIO/SQX_EDGE_PRO.git

# Verifica
git remote -v
# Debe mostrar:
# origin  https://github.com/TU-USUARIO/SQX_EDGE_PRO.git (fetch)
# origin  https://github.com/TU-USUARIO/SQX_EDGE_PRO.git (push)
```

✅ **CONFIRMA**: ¿Remoto vinculado correctamente? (Sí/No)

---

## PASO 5: Commit de configuración

### 5.1 State actual

```bash
cd C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO

git status
# Debe mostrar .gitignore y README.md como changed
```

### 5.2 Stage cambios

```bash
git add .gitignore README.md

# Verifica staged
git status
# Debe mostrar ambos como "Changes to be committed"
```

### 5.3 Commit

```bash
git commit -m "chore: update .gitignore and README for GitHub"

# Verifica
git log --oneline -1
# Debe mostrar tu commit
```

✅ **CONFIRMA**: ¿Configuración commiteada? (Sí/No)

---

## PASO 6: Primera rama y push

### 6.1 Renombra rama principal

```bash
git branch -M main

# Verifica
git branch
# Debe mostrar "* main"
```

### 6.2 Push inicial

```bash
# Primer push (con -u para establecer upstream)
git push -u origin main

# Si pide credenciales:
# Username: tu-usuario-github
# Password: tu-token-personal (ver sección de autenticación abajo)
```

**Validación en GitHub:**
- Ve a https://github.com/TU-USUARIO/SQX_EDGE_PRO
- Refresh página
- Debe mostrar:
  - Branch: `main` (verde)
  - Archivos: README.md, .gitignore, backend/, frontend/, etc.
  - Commit: "chore: update .gitignore and README for GitHub"

✅ **CONFIRMA**: ¿Push exitoso a GitHub? (Sí/No)

---

## ⚠️ AUTENTICACIÓN (Si GitHub pide contraseña)

### Opción A: Token Personal (Recomendado)

1. **Genera token en GitHub:**
   - Perfil → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - New token (classic)
   - **Scopes:** ✅ `repo` (acceso completo a repos)
   - **Expiration:** 90 días (mínimo mantenimiento)
   - Genera y **copia el token**

2. **Usa token como contraseña:**
   ```bash
   git push -u origin main
   # Username: tu-usuario-github
   # Password: [pega el token aquí]
   ```

3. **Guarda credenciales (Windows):**
   ```bash
   git config --global credential.helper wincred
   # Luego, GitHub guardará automáticamente tus credenciales
   ```

### Opción B: SSH (Avanzado)

```bash
# Genera clave SSH
ssh-keygen -t ed25519 -C "tu.email@github.com"

# Abre en notepad
type %USERPROFILE%\.ssh\id_ed25519.pub

# Cópialo y pégalo en GitHub → Settings → SSH Keys

# Usa URL SSH en remoto
git remote set-url origin git@github.com:TU-USUARIO/SQX_EDGE_PRO.git
```

---

## PASO 7: Verifica estado final

### 7.1 En GitHub

Ve a https://github.com/TU-USUARIO/SQX_EDGE_PRO y valida:

```
✅ Branch main (por defecto)
✅ README.md muestra correctamente (renderizado Markdown)
✅ Estructura visible:
   - backend/
   - frontend/
   - desktop/
   - docs/
   - package.json
   - pyproject.toml
✅ .gitignore presente
✅ Última actualización: hace X minutos
```

### 7.2 En tu máquina

```bash
cd C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO

# Log debe mostrar commit en origin/main
git log --oneline -3

# Status debe estar limpio
git status
# "On branch main. Your branch is up to date with 'origin/main'"
```

✅ **CONFIRMA**: ¿Repositorio visible y completo en GitHub? (Sí/No)

---

## PASO 8: Configuración adicional (Opcional pero recomendado)

### 8.1 Rama `develop` (para desarrollo)

```bash
# Crea rama develop localmente
git checkout -b develop

# Push develop al remoto
git push -u origin develop

# En GitHub: Settings → Branches → Change default branch a "develop"
```

### 8.2 Protection rules (Opcional)

En GitHub → Settings → Branches → Add branch protection rule:

**Para `main`:**
- ✅ Require pull request reviews
- ✅ Require status checks to pass

**Para `develop`:**
- ✅ Require pull request reviews (menos restrictivo)

### 8.3 Topics (Tags)

En GitHub → Repo → About (rueda dentada):

**Topics:** `python`, `electron`, `fastapi`, `quantitative-trading`, `metatrader5`

---

## FLUJO FUTURO DE DESARROLLO

Una vez todo esté en GitHub:

### Para trabajar en nuevas features:

```bash
# Asegúrate en develop
git checkout develop

# Crea feature branch
git checkout -b feature/nombre-descriptivo

# Haz cambios, commits
git add .
git commit -m "feat: descripción breve del cambio"

# Sube a GitHub
git push origin feature/nombre-descriptivo

# En GitHub: Crea Pull Request
# - Contra: develop (no main)
# - Descripción: qué cambió y por qué

# Después de revisión/merge: Tu feature está en develop
# Luego se integra a main en releases controladas
```

---

## ✅ CHECKLIST FINAL

- [ ] .gitignore actualizado
- [ ] README.md actualizado
- [ ] Git inicializado localmente
- [ ] Repositorio creado en GitHub
- [ ] Remoto vinculado (`git remote -v` funciona)
- [ ] Primer commit pushed (`git push -u origin main` exitoso)
- [ ] GitHub muestra repo completo y visible
- [ ] Token/SSH autenticación configurada

---

## 🆘 PROBLEMAS COMUNES

### "fatal: could not read Username..."
→ GitHub requiere autenticación (Token o SSH). Ver sección "AUTENTICACIÓN"

### "! [rejected] main -> main (fetch first)"
→ Hay cambios remotos. Ejecuta:
```bash
git pull origin main
git push origin main
```

### "error: failed to push some refs to 'origin'"
→ Probablemente README.md o .gitignore conflictúan. Resuelve:
```bash
git pull origin main --rebase
git push origin main
```

### "Your branch is ahead of 'origin/main' by X commits"
→ Tienes commits locales no pusheados:
```bash
git push origin main
```

---

## 📞 SOPORTE

Si encuentras problemas:

1. **Git help:** `git status` (siempre te dice qué hacer)
2. **GitHub Docs:** https://docs.github.com/en/get-started
3. **Stack Overflow:** Busca el error exacto

---

**Una vez completado, tu repositorio SQX_EDGE_PRO estará público/privado en GitHub y listo para colaboración o deployment.**
