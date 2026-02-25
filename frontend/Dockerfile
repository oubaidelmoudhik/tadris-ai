# ============================================
# Next.js Frontend Dockerfile - Production
# ============================================

# --------------------------------------------
# Base stage
# --------------------------------------------
FROM node:22-alpine AS base

# Install dependencies for native modules
RUN apk add --no-cache libc6-compat

# --------------------------------------------
# Dependencies stage
# --------------------------------------------
FROM base AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# --------------------------------------------
# Builder stage
# --------------------------------------------
FROM base AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build the Next.js application
RUN npm run build

# --------------------------------------------
# Production runner stage
# --------------------------------------------
FROM base AS runner

WORKDIR /app

# Set environment variables
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./

# Set ownership
RUN chown nextjs:nodejs .

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start the Next.js server
CMD ["node", "server.js"]
