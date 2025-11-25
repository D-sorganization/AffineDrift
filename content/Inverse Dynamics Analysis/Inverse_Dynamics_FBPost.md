Post 1

Here's a calculation for a hypothetical scenario I have been considering. The scenario is: what would reverse dynamics tell us for a swing in which force was applied only at one point on the grip, but that point wasn't the mid hands point.

In reverse / inverse dynamics analysis, what we get is an equivalent force and couple at the mid hands point for any given swing. However, we don't exert couples, we exert forces. To determine the equivalent force and couple in "forward" dynamics at a point other than the point of application you essentially compute the moment of the force at both the locations and introduce a "couple" that accounts for the difference. This is mathematically valid and the two bodies would behave exactly the same.

What I find interesting is that for a single force that is applied off of the point of analysis in inverse dynamics, the result you would get would be a force and a couple, despite only applying a force.

It is very tempting to see a force and couple from inverse dynamics reported and to think it means that you need to push or pull to match the force component and then to twist on it to match the couple component. Unfortunately I don't think this is an entirely valid assumption to make.

Obviously a single force never exists on a real golf club, but where we apply force to the club with our hands can change. For example we can pull with the pinky of the left hand or with the forefinger. We can push with the palm of the right hand or through the forefinger. Where these points of force application are relative to the midpoint of the hands are can meaningfully change the interpretation of the results one would get from reverse dynamics.

I've also shown an example of how the equivalent couple for a set of forces would change for forces of the same magnitude but applied by different parts of the hands. The equivalent couple here changes by about 15%. (In the calculation positive forces are up and positive torques are clockwise).

Post 2

Here's some analysis I've done regarding how we can evaluate the meaning of the net force and couple that we get from reverse / inverse dynamics analysis. I think it could have some bearing on the alpha debate and can give a bit of framework to help understand how to translate real life implications from calculated values.

Essentially, the reverse dynamics process gives a value of a force and couple at a point on the club. Typically the midpoint. This does not paint a true picture of reality as we do not exert our force at the midpoint in all cases. We exert forces at various points along the club. When we exert force somewhere along the club that is not the midpoint, it is possible to adjust the force and couple from the midpoint to a new force and couple at a different point of interest. This is done by keeping the sum of forces and sum of moments between the two points constant and solving straightforward algebraic equations.

The question then arises of "where should we look at the force and couple?". I think that a good answer to that question is found with the following method using forward dynamics type reasoning.

1. Recognizing that there are multiple forces applied to the club on multiple sides, resolve these forces into equivalent forces acting on either side of the shaft. There is a mathematical way of doing this that involves summing the moments of each, but the exact details are not particularly important to this theoretical argument. What is important is that at the end of this process you are left with a force acting on either side of the shaft representing the sum of all forces acting on that side of the shaft after this process.

2. Break this pair of forces down into a couple and a net force by simple vector addition / subtraction. This will leave you with two equal magnitude forces and the "leftovers" from the process which is the net force. The net force will be at whichever point in which the magnitude of the force was higher between the two vectors.

3. Recognize that the couple is a "free vector" and can be moved to act anywhere on the body without changing the rotational behavior of the body. The leftover force cannot. Due to this, the equivalent force and couple should be evaluated at this point where the force is left over in the forward dynamics generation of a couple.

4. Take reverse dynamics data and imagine completing this process in reverse to get back to a set of forces that represents reality as best as possible. To do so you would need information that you don't have like the distribution of the point of application of forces to the grip.

It would seem that through this we haven't really done much as we don't have the data to go backwards from reverse dynamics to parse out the forces that we actually applied to the club. However, we can do two different things despite the limitations - 1. Set general bounds on the error of our assumptions to create a range of possible inputs for a set of reverse dynamics data, and 2. Conduct "what if" analysis. 

I have included a calculation of the bounds for the error if the point of application of force moves up and down the grip (first picture), as well as a couple of "what if" scenarios where a set of reverse dynamics data is assumed and comparisons are made between cases where the points of application of force on the club were different (last two pictures).

How I think this would apply to the alpha debate is illustrated in the last picture showing a late downswing position in which reverse dynamics gives us a result of positive moment of force and negative couple. Depending on the magnitude of the moment of force, the couple, and the point of force application, a sign change in the couple at the point of interest is mathematically possible despite reverse dynamics data giving a "negative couple" at the midpoint of the grip. 

Is it probable? Probably not. But the numerical values can definitely change.