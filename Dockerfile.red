FROM nodered/node-red:latest
RUN npm install --no-update-notifier --no-fund --only=production \
    node-red-dashboard \
    aedes \
    aedes-persistence-level
