# Slack Setup Guide

Slack requires a few more steps because we use **Socket Mode**. This allows the bot to run locally or on your home server without needing a public IP or webhooks.

## Step 1: Create the App
1. Go to the [Slack API Dashboard](https://api.slack.com/apps).
2. Click **Create New App** -> **From scratch**.
3. Name it (e.g., `Nuroly-Observer`) and select your workspace.

## Step 2: Enable Socket Mode (App Token)
1. In the left menu, click **Socket Mode**.
2. Toggle **Enable Socket Mode** to **On**.
3. Create an App-Level Token (Name it whatever you want, add the `connections:write` scope).
4. Copy the token starting with `xapp-...` and paste it into your `.env` file as `SLACK_APP_TOKEN`.

## Step 3: Set Permissions (Bot Token)
1. Go to **OAuth & Permissions** in the left menu.
2. Scroll down to **Scopes** -> **Bot Token Scopes**.
3. Add the following scopes:
   * `chat:write` (to send messages)
   * `channels:history` (to read public channels)
   * `groups:history` (to read private channels)
   * `im:history` (to read direct messages)

## Step 4: Enable Event Subscriptions
1. Go to **Event Subscriptions** in the left menu.
2. Toggle **Enable Events** to **On**.
3. Scroll down to **Subscribe to bot events** and add:
   * `message.channels`
   * `message.groups`
   * `message.im`
4. Click **Save Changes** at the bottom!

## Step 5: Enable the Chat Window (App Home)
1. Go to **App Home** in the left menu.
2. Scroll to the bottom (**Show Tabs** section).
3. Ensure the **Messages Tab** is checked.
4. **Important:** Check the box that says *Allow users to send Slash commands and messages from the messages tab*.

## Step 6: Install & Get Bot Token
1. Go to **Install App** in the left menu and install it to your workspace.
2. Copy the **Bot User OAuth Token** starting with `xoxb-...` and paste it into your `.env` file as `SLACK_TOKEN`.

## Step 7: Get your Slack Member ID (For Whitelisting)
1. Open your Slack client.
2. Click on your profile picture -> **Profile**.
3. Click the three dots (**More**) -> **Copy member ID** (Usually starts with `U` or `W`).
4. Paste this ID into your `.env` file as `SLACK_ALLOWED_USERS`.