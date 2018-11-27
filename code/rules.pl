:- dynamic on/2.
:- dynamic top/1.

put_on(A,B) :- on(A,B).
put_on(A,B) :-
     not(on(A,B)),
     A \== table,
     A \== B,
     top(A),
     top(B),
     on(A,X),
     retract(on(A,X)),
     assert(on(A,B)),
     assert(move(A,X,B)).

top(table).

top(A) :- not(on(_X,A)).

top(A) :-
     A \== table,
     on(X,A),
     top(X),
     retract(on(X,A)),
     assert(on(X,table)),
     assert(move(X,A,table)).

do(Goalslist) :- valid(Goalslist), do_all(Goalslist,Goalslist).

valid(_).

do_all([G|R],Goals) :- call(G), do_all(R,Goals),!.

do_all([G|_],Goals) :- achieve(G), do_all(Goals,Goals).

do_all([],_Goals).

achieve(on(A,B)) :- put_on(A,B).
