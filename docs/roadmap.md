# Roadmap

This is a list of features I would like to see and develop for Diagraph.

I welcome feedback on any and all of this. Feel free to open a Github Discussion if you'd like to suggest alternative directions / express support for a specific feature.

## Saving / Loading
Support saving and loading from `pkl` formats and `json` formats. Support saving / loading either just the graph, or the graph + state.

This will enable going from, say, iteration in a Jupyter notebook directly to production code. 

Alternatively, a user would have to copy / paste code from their notebook into their production code.

It would also support saving in progress graphs for sharing or later inspection.

## Historical State

Right now a Diagraph only stores the latest iteration of state (results, inputs, prompts, etc.)

It would be great if you could step through all changes of a Diagraph, so that if there is a particular prompt or result, it's not lost during subsequent iterations.

## Visualization extras

There's ways we could improve Diagraph visualizations. Here are some ideas:

- Better visual design at a glance (for example, use color to showcase node state like success, errors, not-run-yet, etc.)
- Explore editablity of the graph via the node editor (not sure how this would play with something like a Jupyter notebook)
- Live updates (see a graph update as it's iterating; again, not sure how this would play with Jupyter notebooks)
- ASCII tree visualization, for CLI or terminal use cases
- Ability to boot up a live, local server, and get pretty private HTML output
- Rewrite visualization to a web component from React (lighterweight, particularly in a Jupyter notebook)

## Result Coercion

LLMs don't always respond how we want them to.

I think a useful pattern would be the ability to specify a type in a return signature and have Diagraph automatically coerce the return type.

I could imagine a few buckets:

- simple type coercion: things like strings, ints, booleans, etc.
- Pydantic models, or more complicated structures (could be particularly useful for validating, say, a function call response from OpenAI)
- functions - more complicated checks validating a response, e.g. checking that a SQL statement is valid SQL
- LLM-powered functions - use an LLM to validate an LLM. For example, for a function `tell_me_a_joke`, specify a return type of `is_this_joke_funny`

## Editing a graph's structure

Right now, once a graph is instantiated, its layout cannot be edited (the nodes' properties can be edited).

It could potentially be useful to be able to subsequently add nodes, remove nodes, rewrite node edges, etc.

I don't know how this would play nicely with the current design pattern of declaring dependencies within a function. I also don't know if this is particular helpful or if just re-instantiating the Diagraph with new nodes is sufficient.

## Dynamic Graphs

Right now, we only support static structured dialogues.

There are many many use cases that could benefit from dynamic control flows. Things like while loops, for loops, if/else statements, etc.

I don't see a great way to support this sort of thing given the current design strategies for building a Diagraph. It would also make visualizing harder.

Right now, there's a 1:1 relationship between the graph _template_ (the not-yet-run graph) and the graph's state (the run graph). There's not really a distinction between the two, which makes it possible to do something like `diagraph[some-node].result`.

If a graph becomes dynamic, this pattern disappears, which adds quite a bit of extra complication.
