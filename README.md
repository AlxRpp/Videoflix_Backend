# Videoflix Backend

A Django REST backend for a small video streaming platform. Users register and
sign in, and every uploaded video is automatically converted into several
resolutions and prepared for adaptive streaming (HLS), so the frontend can play
it back smoothly and let the viewer switch quality.

The whole stack runs in Docker – one command and it is up.

---

## What it does

- **Accounts** – registration with email activation, login/logout, password
  reset. Authentication uses JWT stored in **httpOnly cookies**.
- **Video upload** – an admin uploads a video in the Django admin.
- **Background processing** – on upload, a worker automatically:
  - generates a **thumbnail** from the video,
  - converts it to **480p, 720p and 1080p**,
  - splits each resolution into **HLS** (`index.m3u8` + `.ts` segments).
- **Streaming API** – the frontend fetches the video list, the HLS playlist and
  the single segments per resolution.

Heavy work (ffmpeg) never blocks the request – it runs in a background queue.

---

## Tech stack

| Area | Technology |
|------|------------|
| Language | Python 3.12+ |
| Framework | Django 6, Django REST Framework |
| Auth | SimpleJWT (cookie based) |
| Database | PostgreSQL |
| Cache & queue | Redis (Django cache + RQ broker) |
| Background jobs | Django RQ |
| Video processing | ffmpeg |
| Serving | Gunicorn + WhiteNoise |
| Containerization | Docker / Docker Compose |

---

## Requirements

- **Docker** and **Docker Compose**
- Python **3.12+** – only needed if you ever run the project *without* Docker;
  the Docker image already ships with it.

> ffmpeg, PostgreSQL and Redis all run inside the containers, so you don't have
> to install anything besides Docker.

---

## Getting started

**1. Clone the repository**

```bash
git clone <your-repo-url>
cd Videoflix_Backend
```

**2. Create your environment file**

```bash
cp .env.example .env
```

Then open `.env` and fill in the values (see the table below). In particular,
**generate your own `SECRET_KEY`**, for example:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

and paste the result into the `SECRET_KEY` line. The project still runs with the
placeholder from `.env.example`, but for a real deployment you should use your
own key.

**3. Build and start everything**

```bash
docker compose up --build
```

On the first start the container automatically:
- waits for PostgreSQL,
- runs the migrations,
- creates a superuser from your `DJANGO_SUPERUSER_*` values,
- starts the RQ worker and the web server.

**4. Open the app**

- Admin: <http://localhost:8000/admin/>
- API root: <http://localhost:8000/api/>

Log in to the admin with your superuser credentials and upload a video – the
thumbnail and all resolutions are generated in the background.

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development |
| `ALLOWED_HOSTS` | Comma separated list of allowed hosts |
| `CSRF_TRUSTED_ORIGINS` | Comma separated list of trusted origins |
| `DJANGO_SUPERUSER_USERNAME` / `_EMAIL` / `_PASSWORD` | Auto-created admin account |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL connection |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` / `REDIS_LOCATION` | Redis connection |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP settings |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` / `DEFAULT_FROM_EMAIL` | Email options |
| `EMAIL_BACKEND` | Controls how emails are sent (see the note below) |

### Email sending

By **default** emails are sent over **SMTP**, using the `EMAIL_*` values above –
the project is production-ready out of the box.

For **local testing** you usually don't have a real mail server. In that case,
**uncomment the `EMAIL_BACKEND` line** in your `.env`:

```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Django then prints the activation and password-reset **links straight to the
container logs** instead of sending them. You can watch them with:

```bash
docker compose logs -f web
```

---

## API overview

All endpoints are prefixed with `/api/`.

### Accounts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register/` | Register a new (inactive) user and send an activation email |
| GET | `/activate/<uidb64>/<token>/` | Activate the account via the emailed link |
| POST | `/login/` | Log in, sets the JWT cookies |
| POST | `/logout/` | Log out and clear the cookies |
| POST | `/token/refresh/` | Get a fresh access token from the refresh cookie |
| POST | `/password_reset/` | Send a password reset email |
| POST | `/password_confirm/<uidb64>/<token>/` | Set a new password via the emailed link |

### Videos
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/video/` | List all videos (metadata + thumbnail) |
| GET | `/video/<movie_id>/<resolution>/index.m3u8` | HLS playlist for a video in a resolution |
| GET | `/video/<movie_id>/<resolution>/<segment>/` | A single HLS segment (`.ts`) |

All video endpoints require authentication (JWT cookie).

---

## How a video becomes streamable

1. An admin uploads a video in the Django admin.
2. A `post_save` signal queues background jobs (Django RQ).
3. The worker runs ffmpeg to create the thumbnail, the three resolutions and the
   HLS segments, storing everything under `media/`.
4. The frontend requests the playlist and the player pulls the segments one by
   one.

---

## Notes

- This repository contains the **backend only**. The frontend is a separate
  project and was provided by the Developer Akademie.
- Uploaded media lives in a Docker volume, so a fresh clone starts with an empty
  library – upload a video to test the full flow.
