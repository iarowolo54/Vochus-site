# Deploying the Vochus Easy Save website (DirectAdmin, GO54 hosting)

The site is static HTML plus one PHP file (`send.php`) that emails the Contact and Agent-application forms to
info@vochuseasysave.com. Everything below is done in the DirectAdmin panel (your GO54 DirectAdmin panel) and takes about
20 minutes. No developer tools are needed.

## 0. Build the package (developer step)

```
python3 _tools/package.py
```

This creates `dist/vochus-website-YYYYMMDD.zip` with only the files that belong on the server. Send that zip to
whoever does the upload.

## 1. Remove the placeholder Node.js app first

Today `public_html` holds a GO54 parking page and a stub Node.js (Passenger) app. Its `.htaccess` sends every unknown
URL to that stub, which would hide our 404 page and could interfere with `send.php`.

1. DirectAdmin → **Setup Node.js App**. If an application is listed for vochuseasysave.com, **Stop** it, then **Delete** it.
   Deleting it removes the Passenger lines from `.htaccess`.
2. DirectAdmin → **File Manager** → `domains/vochuseasysave.com/public_html`. Open `.htaccess` (enable "show hidden
   files" if needed). It must contain **no** lines starting with `Passenger` or `PassengerAppRoot`. If it still does,
   delete the whole `.htaccess` file. Ours replaces it in the next step.
3. In the same folder, delete GO54's `index.html` and `logo.svg`.

## 2. Upload the site

1. File Manager → `domains/vochuseasysave.com/public_html` → **Upload** → choose `vochus-website-YYYYMMDD.zip`.
2. Right-click the zip → **Extract** (into this folder). You should now see `index.html`, `send.php`, `assets/`,
   `.htaccess` and the other pages directly inside `public_html`. Delete the zip afterwards.
3. Still in File Manager, go **up one level** to `domains/vochuseasysave.com/` and create a folder named
   `vochus-data`. It sits beside `public_html`, not inside it, so it is never served to the public. `send.php` keeps its
   small rate-limit file there. (If the folder cannot be created, `send.php` falls back to the system temp folder.)

## 3. PHP version

DirectAdmin → **Select PHP Version** (CloudLinux). Choose **8.1 or newer** (8.2 or 8.3 preferred) and save. Default
extensions are enough; `mbstring` is recommended.

## 4. Email: the sending address and deliverability

The forms send from `no-reply@vochuseasysave.com` and deliver to `info@vochuseasysave.com`.

1. DirectAdmin → **E-mail Manager → E-mail Accounts** → create `no-reply@vochuseasysave.com` (any strong password; nobody
   needs to log into it). Confirm `info@vochuseasysave.com` exists or forwards somewhere that is read.
2. DirectAdmin → **E-mail Manager** (or **DNS Management**) → enable **DKIM** for the domain, and make sure the **SPF**
   record includes this server (DirectAdmin usually adds `v=spf1 a mx ip4:<server> ~all` when DKIM/SPF is enabled). Both
   stop the form emails landing in spam.
3. To change the recipient or sender later, edit `send-config.php` in `public_html` (two lines at the top).

## 5. Test

1. Open https://vochuseasysave.com/ (and http:// and www.): all must land on `https://vochuseasysave.com/`.
2. Open https://vochuseasysave.com/does-not-exist: you must see **our** 404 page ("Sorry, we could not find that page"),
   not "It works! NodeJS". If you see the Node text, step 1 was not completed.
3. Contact page → fill the form → **Send Message**. You should see "Thank you. Your message has been sent." in place of
   the form, and the message should arrive at info@vochuseasysave.com within a minute, with the sender's address in
   Reply-To.
4. Become an Agent page → fill the application → **Submit Application**. Same check.
5. Submit one form with JavaScript disabled (or from a very old browser): you should land on `thanks.html`.

## 6. If mail does not arrive

- Check the spam folder of info@vochuseasysave.com first.
- Confirm step 4 (the `no-reply@` account exists and DKIM/SPF are on). Shared hosts often refuse `From` addresses that
  are not real mailboxes on the server.
- DirectAdmin → **E-mail Manager → Mail queue / Delivery logs** (if offered by the host) shows whether the server accepted
  the message.
- If the host blocks PHP `mail()` or deliverability stays poor, the fix is to send over SMTP instead: in `send.php`
  replace the body of `send_mail()` with an SMTP client (PHPMailer, or the host's SMTP relay) using the `no-reply@`
  mailbox credentials. Nothing else on the site changes.
- Submissions are limited to 5 per visitor per hour; a tester who hits the limit sees "Too many messages from this
  connection" and should wait an hour (or delete `vochus-data/rate.json`).

## 7. Updating the site later

Rebuild the zip, upload and extract again (files overwrite in place). `send-config.php` and `.htaccess` are included in
the package, so if they were edited on the server, re-apply those edits.

## Notes

- Canonical URLs use `https://vochuseasysave.com/` (apex). `.htaccess` redirects `www.` to the apex; if the site should
  live on www instead, remove that rule and change `SITE` in `_tools/assemble.py`, then rebuild.
- The Vochus app itself lives at `easysave.vochusglobalservices.co.uk`; all app links on the site point there, so
  there is no routing conflict with this domain.
- `.htaccess` sets a Content Security Policy that allows only this site's own files. If a third-party script (analytics,
  chat widget) is added later, its host must be added to `script-src`/`connect-src`.
