FROM redis

# Copy config file
COPY redis.conf /etc/redis/redis.conf

# Expose port
EXPOSE 6379

# Command to run on start
CMD [ "redis-server", "/etc/redis/redis.conf" ]
