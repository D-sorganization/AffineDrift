# DNS Configuration for GitHub Pages Custom Domain

## Current Setup
- **Repository**: D-sorganization/AffineDrift
- **Custom Domain**: www.affinedrift.com
- **CNAME File**: ✅ Correctly configured in repository

## DNS Configuration Required

You need to configure DNS records at your domain registrar (where you purchased affinedrift.com).

### Option 1: CNAME Record (Recommended for www subdomain)

At your domain registrar, add a **CNAME record**:

```
Type: CNAME
Name: www
Value: d-sorganization.github.io
TTL: 3600 (or default)
```

This will point `www.affinedrift.com` to your GitHub Pages site.

### Option 2: A Records for Apex Domain

If you also want to use `affinedrift.com` (without www), add **A records**:

```
Type: A
Name: @ (or leave blank)
Value: 185.199.108.153
Value: 185.199.109.153
Value: 185.199.110.153
Value: 185.199.111.153
TTL: 3600
```

**Note**: GitHub's IP addresses may change. Check [GitHub Pages documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site#configuring-an-apex-domain) for current IPs.

## Verification Steps

1. **Add DNS records** at your domain registrar (Namecheap, GoDaddy, etc.)
2. **Wait for DNS propagation** (can take up to 48 hours, usually much faster)
3. **Check DNS propagation**: Use tools like:
   - https://dnschecker.org
   - `nslookup www.affinedrift.com`
   - `dig www.affinedrift.com`
4. **Verify in GitHub**: Go to repository Settings → Pages → Custom domain
   - Should show "DNS check successful" when configured correctly

## Troubleshooting

### If DNS is configured but GitHub still shows error:
1. Wait a few hours for DNS propagation
2. Clear browser cache
3. Check that CNAME record points to: `d-sorganization.github.io` (not `d-sorganization.github.io/AffineDrift`)
4. Verify no conflicting DNS records exist

### Temporary Solution:
If you want to use the default GitHub Pages URL while fixing DNS:
- Remove or rename the `CNAME` file
- Site will be available at: `https://d-sorganization.github.io/AffineDrift/`

## Current Status
- ✅ CNAME file in repository: Correct
- ❌ DNS records at registrar: Need to be configured
- ⏳ Waiting for DNS propagation after configuration

