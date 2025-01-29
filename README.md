
# Building Similarities

### Back to Basics: TF-IDF

You can consider each public deck as a document and each card as a token. By making this simple transformation, you can represent all the decks you have using a TF-IDF vector representation. Once you have this vector representation, you can easily calculate pairwise similarities using cosine similarity.

### Thinking in a Probabilistic Manner

Using the same idea of treating a deck as a document and a card as a token, you can perform a simple vectorization (using binary values: 1 or 0, not counting frequency) to calculate both the Jaccard distance and conditional probability.

- We use the Jaccard implementation because it is easily optimized for sparse matrices.
- We will modify the Jaccard method to obtain the desired outcome.
- This is a "Score," not truly a similarity or a distance.
- This score is not commutative.


# Building our deck

### Building the Synergy Score of a Deck from Pairs

When you play commander, you learn that the most important synergy is the individual synergy between the "99" and the commander. Within a deck, there are multiple combos/clusters.

Taking this knowledge into consideration, we propose the following formula:

F(card, Deck, commander) = s(card, commander) + Sum(s(card, deck_i))

To account for these "clusters," the second term can be reduced to the top K synergies each card has with the deck.

The total Synergy of a deck would be:

SUM(F(card, Deck, commander)) for each card in (commander, deck)

### How to Build the Deck?

- Too many creatures?
- Not enough mana?

Simply use the data and some nonparametric statistics.

Once we decide on our commander and the "flavor" cards (cards that we want to include no matter what), we can create a distribution for each decision:

1. Should we go with the standard 36 mana deck? Maybe lower (e.g., elves)? Or higher (landfall or land-focused decks)?
2. How many creatures? More than 30 (e.g., elves)? Is 13 enough? (e.g., fAIeries)

# Optimizing and Building Decks

1. Define Commander
2. Define Score System
3. Define Flavor
4. Calculate Lands/Mana Distribution
5. Calculate Expected Distribution by Converted Mana Cost and Card Type
6. Define K

To optimize, we start by selecting the cards that maximize the total synergy of the deck.

- First approach: Fully greedy
- Second approach: Inspired by Beam search but simplified and greedy

We follow these steps:

- Select the top k_2 cards that add the most individual synergy to the deck.
- Create overlapping groups of size k_3 to determine which group to include.
- Update the deck with the selected group.

We repeat the process until the deck is complete.

The CMC (converted mana cost) and card type distribution may start to fail in the final rounds. We exclude cards that cannot be included due to the upper limits of the distribution:

- If the deck has 10 instants and the upper limit for that card type is 10, we exclude instants from the list of potential cards to include.

This process does not ensure a deck with the maximum synergy. After the first round, you might find some good candidate cards left out. You can repeat the process by starting the optimization with the resulting deck from the first round and excluding the cards with the least synergy.