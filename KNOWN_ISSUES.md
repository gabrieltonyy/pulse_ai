# Pulse AI — Known Issues

**Purpose:** Track bugs, blockers, and unresolved issues.

---

## Current Issues

None currently. Phase 1 is scaffold-only with no implementation yet.

---

## Resolved Issues

None yet.

---

## Future Considerations

### Dependency Conflicts
- SQLAlchemy version must be <2.0.36 for langchain-community compatibility
- Monitor for updates to langchain packages

### API Rate Limits
- Ticketmaster: 5000 requests/day
- Geoapify: Depends on plan
- OpenWeather: 1000 requests/day (free tier)
- Need to implement proper rate limiting and caching

### Performance
- Multiple external API calls per search
- Need to optimize with parallel requests
- Consider caching strategy

### Testing
- Need to mock external APIs for tests
- Demo mode data needs to be comprehensive
- Integration tests require test database

---

## Notes

This file will be updated as issues are discovered during implementation.