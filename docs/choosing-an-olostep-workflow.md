# Start with the input and the outcome

| You have / need | Starting surface | Decision to make |
|---|---|---|
| One known URL, content now | Scrape | Which output format does the consumer need? |
| Many known URLs | Batch | Can you wait asynchronously and handle partial results? |
| A domain, need URL discovery | Map | What scope should be included? |
| A site to traverse | Crawl | What page/depth limits are appropriate? |
| A natural-language discovery query | Search | Do you need results only or scraped content too? |
| A source-backed synthesis | Answers | How will you inspect the sources and uncertainty? |
| Repeated observation | Monitors / schedules | What constitutes a meaningful change? |

This repository implements only the known-URL batch path. Search is a useful
follow-on, but combining discovery and extraction makes it harder to explain which
stage caused missing content. Separating those concerns makes this sample teachable.

Reference: https://docs.olostep.com/get-started/welcome
