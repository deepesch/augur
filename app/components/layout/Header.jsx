let React = require('react');
let Fluxxor = require("fluxxor");
let FluxMixin = Fluxxor.FluxMixin(React);

let SendModal = require("../SendModal");
let SendCashModal = SendModal.SendCashModal;
let SendRepModal = SendModal.SendRepModal;
let SendEtherModal = SendModal.SendEtherModal;

let Button = require('react-bootstrap/lib/Button');

let Router = require("react-router");
let Link = Router.Link;

let utilities = require("../../libs/utilities");
let BigNumber = require("bignumber.js");

let Header = React.createClass({
    mixins: [FluxMixin], // only to dispatch action

    handleSignInClick(event){
        event.preventDefault();
        this.props.toggleSignInModal();
    },
    handleRegisterClick(event){
        event.preventDefault();
        this.props.toggleRegisterModal();
    },
    handleSendCashClick(event){
        event.preventDefault();
        this.props.toggleSendCashModal();
    },
    handleSendRepClick(event){
        event.preventDefault();
        this.props.toggleSendRepModal();
    },
    handleSendEtherClick(event){
        event.preventDefault();
        this.props.toggleSendEtherModal();
    },

    handleSignOutClick: function (event) {
        event.preventDefault();
        this.getFlux().actions.config.signOut();
    },
    getCashText() {
        let hasCash = this.props.asset.cash && this.props.asset.cash.gt(new BigNumber(0));
        if (!hasCash && this.props.isNewRegistration) {
            return "coming";
        } else {
            return this.props.asset.cash ? this.props.asset.cash.toFixed(2) : '-';
        }
    },
    getRepText() {
        let hasRep = this.props.asset.reputation && this.props.asset.reputation.gt(new BigNumber(0));
        if (!hasRep && this.props.isNewRegistration) {
            return "coming";
        } else {
            return this.props.asset.reputation ? this.props.asset.reputation.toFixed(2) : '-';
        }
    },
    getEtherText() {
        let hasEther = this.props.asset.ether && this.props.asset.ether.gt(new BigNumber(0));
        if (!hasEther && this.props.isNewRegistration) {
            return "coming";
        } else {
            return this.props.asset.ether ? utilities.formatEther(this.props.asset.ether).value : '-';
        }
    },
    render() {
        let isUserLoggedIn = this.props.userAccount;
        let menuItemsOnLeft, menuItemsOnRight;

        if (isUserLoggedIn) {
            menuItemsOnLeft = (
                <ul className="nav navbar-nav">
                    <li>
                        <Link to="markets">
                            Markets ({ this.props.marketsCount })
                        </Link>
                    </li>
                    <li>
                        <Link to="ballots">
                            Ballots ({ this.props.ballotsCount })
                        </Link>
                    </li>
                    <li>
                        <a href="#" onClick={this.handleSignOutClick}>
                            Sign out
                        </a>
                    </li>
                </ul>
            );

            let cashBalance = this.getCashText();
            let repBalance = this.getRepText();
            let etherBalance = this.getEtherText();
            menuItemsOnRight = (
                <ul className="nav navbar-nav navbar-right">
                    <li>
                        <a href="#" className="" onClick={this.handleSendCashClick}>
                            cash {cashBalance}
                        </a>
                    </li>
                    <li>
                        <a href="#" className="" onClick={this.handleSendRepClick}>
                            rep {repBalance}
                        </a>
                    </li>
                    <li>
                        <a href="#" className="" onClick={this.handleSendEtherClick}>
                            ether {etherBalance}
                        </a>
                    </li>
                </ul>
            );
        } else {
            menuItemsOnLeft = (
                <ul className="nav navbar-nav">
                    <li>
                        <Link to="markets">
                            Markets ({ this.props.marketsCount })
                        </Link>
                    </li>
                </ul>
            );

            menuItemsOnRight = (
                <ul className="nav navbar-nav navbar-right">
                    <li>
                        <a onClick={this.handleSignInClick}>Sign in</a>
                    </li>
                    <li>
                        <a onClick={this.handleRegisterClick}>Register</a>
                    </li>
                </ul>
            );
        }

        return (
            <nav className="navbar" role="navigation">
                <div className="container">
                    <div className="navbar-header">
                        <a href="#" type="button" className="navbar-toggle collapsed" data-toggle="collapse"
                                data-target="#navbar-main-collapse">
                            <strong>Menu</strong>
                        </a>
                        <Link className="navbar-brand" to="overview">
                            Augur
                        </Link>
                    </div>

                    <div className="collapse navbar-collapse" id="navbar-main-collapse">
                        { menuItemsOnLeft }
                        { menuItemsOnRight }
                    </div>
                </div>
            </nav>
        );
    }
});

module.exports = Header;
