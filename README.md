# aio-bernhard
An asyncio riemann wrapper based on [https://github.com/banjiewen/bernhard](https://github.com/banjiewen/bernhard)  

TCP Only for Now using [AsyncIO Stream](https://docs.python.org/3/library/asyncio-stream.html)  

Opens a connection on every send

Use the same as [bernhard](https://github.com/banjiewen/bernhard), but with await  

```
import aiobernhard

c = bernhard.Client()
await c.send({'host': 'myhost.foobar.com', 'service': 'myservice', 'metric': 12})
```

###TO DO
- [ ] UDP Transport
- [ ] Query
- [ ] SSL Transport

