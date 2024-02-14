# Bucket


Bucket is a python library to create nicer functional coverpoints. There are several benefits writing the coverage in python, such as:

* Easier integration into cocotb and other python testbenches
* No commercial EDA license required
* Vendor independence - easily collect coverage from multiple tools/sources (eg. models, log parsers, etc)

## Documentation:
[Read the Documentation](docs/index.md)

## Support
This library is being actively built, and is expected to change while it matures and key features are added.
We are not providing external support for use of this library, however we are aiming to make it as easy to use as possible. 

As per the licence: 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Roadmap
There are several features planned but not actively started. These include:

- Linter / CI
- Improved documentation
- Use logging instead of print
- Coverage filtering to enable only coverpoints of interest
- Tiered coverage to allow for quicker CIs, more granuality for soak regressions, etc
- Improved coverage viewer
- Track which testcases contribute to coverage
- Speed optimisations

## Contributions

**We will be introducing a contributor licence agreement in the near future. In the meantime, if you want to contribute please get in touch.**

Please feel free to contribute to the project, following these guidelines:

* Please contribute by creating a fork and submitting a pull request.
* Pull requests should be as small as possible to resolve the issue they are trying to address.
* Pull requests must respect the goals of the library, as stated in the documentation.
* Pull requests should take care not to make performance worse except for cases which require bug fixes.
* Pull requests should update the documentation for any added/changed functionality.

