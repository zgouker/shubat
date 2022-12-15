# Changelog

## [Unreleased]

## 1.2.1 - 2022-11-28
- Created changelog
- Patch bug with incorrect tracking date for art messages

## 1.2.0 - 2022-11-xx

- Ported backend from python dictionaries to sqlite database
- Refactored repost police bot to use sqlite backend
    - As a result, recovery is now graceful and no longer needs to re-scan entire discord channel history
- Refactored stats compilation to use sqlite backend
    - As a result, compilation is now an aggregation query and no longer needs to re-scan discord channel history
- Initial download picture script
- Added information of poster and characters in repost message
- Factored some common code into utils library

## 1.1.0 - 2022-10-xx

- to be backfilled

## 1.0.0 - 2022-10-xx

- To be backfilled