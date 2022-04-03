# Formal verification of BokkyPooBah's DateTime library

As part of a customer engagement, our engineers verified the correctness of a dependency, [BokkyPooBah's DateTime library](https://github.com/bokkypoobah/BokkyPooBahsDateTimeLibrary). Because this library is used by many Solidity projects, we have released our verification of this library for the public.

This subdirectory contains artifacts from experiments described originally in this [Twitter thread](https://twitter.com/Zellic_io/status/1510341868021854209).

We verified the correctness of the core function `_daysToDate` in the contract BokkyPooBahsDateTimeLibrary. We verified `_daysToDate` by comparing it against the function [`__secs_to_tm`](https://github.com/rofl0r/musl/blob/master/src/time/__secs_to_tm.c) in [musl libc](https://musl.libc.org/). This function is used to implement gmtime in musl libc. **No attempt was made to verify other behavior of the DateTime library outside of this function.**

### Brute-force Python verification against `datetime`

We ported the `_daysToDate` function to Python and verified it by checking it against Python's built-in `datetime` module as a ground truth.

See `verify_python.py` for code. This conducts a brute-force verification for a range of timestamps ranging +/- 30 years from the current date.

This is not very fast (it's Python), but it provides a basic level of assurance for the correctness of the function against Python's datetime library, which, in CPython is implemented with `gmtime`.

### Manual verification with Z3Py

We ported `__secs_to_tm` from C to Python, and `_daysToDate` from Solidity to Python. Then we used the implementations to generate a SMT expression with Z3Py (the Python bindings for the Z3 solver).

The code for this experiment is found in `z3py_verify.py`. Some modifications were required to the musl libc function `__secs_to_tm`. First, the function originally contained a for-loop. This was unrolled manually to simplify the SMT formula to expedite verification. Secondly, variables are frequently introduced manually, in a style similar to global value numbering or SSA, in order to limit the size of SMT expressions.

We elect to export the SMT formulas to a generic smtlib2 file (verify.smt2), and run an external solver rather than Z3. We ran cvc5 against the generated equations. The ultimate command line used was `cvc5-Linux verify.smt2`.

### Verification with angr or manticore

Unfortunately, we attempted to verify the implementations in C (with angr and manticore) and Solidity (with manticore) but did not succeed. The solvers did not complete in a timely fashion and we abandoned this experiment.

### Verification with solc's SMTChecker

We ported `__secs_to_tm` from C to Solidity, and added assertions to verify that the results agreed with `_daysToDate`. We checked this using solc's SMTChecker in BMC mode with CVC4 solver. We compiled solc from source to enable CVC4, version `0.8.14-develop.2022.4.2+commit.c4909e99.Linux.g++`. We also attempted to use CHC mode, but it did not converge in time.

The command line used was `solc --model-checker-div-mod-no-slacks --model-checker-timeout 0 --model-checker-solvers cvc4 --model-checker-engine bmc SMTCheckerVerification.sol`.

### Limitations

When porting code from Solidity to other languages, there may be slight semantic differences introduced. For example, in Python, integers do not overflow, whereas they may in Solidity.

Our verification found no discrepancies; however, the reader should be aware of this caveat.

### Disclaimer

This assessment does not provide any warranties on finding all possible issues within its scope; i.e., the evaluation results do not guarantee the absence of any subsequent issues. Zellic, of course, also cannot make guarantees on any additional code added to the assessed project after our assessment has concluded. Furthermore, because a single assessment can never be considered comprehensive, we always recommend multiple independent assessments paired with a bug bounty program. Finally, this assessment report should not be considered as financial or investment advice.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### License

All code within this subdirectory is licensed under the [MIT License](https://opensource.org/licenses/MIT). The foregoing statement does not apply to other files, documents, or code contained elsewhere within this repository.
