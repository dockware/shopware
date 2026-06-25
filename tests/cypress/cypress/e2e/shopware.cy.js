import Shopware from "Services/Shopware";
import AdminActions from "Actions/AdminActions";

const shopware = new Shopware();
const adminAction = new AdminActions();


beforeEach(() => {
    cy.viewport(1920, 1080);
})

describe('Shopware Storefront', () => {

    it('Shopware Storefront is available', () => {

        cy.visit('/');

        cy.contains('Realised with Shopware');
    })

    it('Shopware Storefront navigation is working', () => {

        cy.visit('/');

        cy.get('.nav-item-a515ae260223466f8e37471d279e6406 > .main-navigation-link-text > span').click();

        cy.contains('Main product with properties');
    })

    it('Symfony Debug toolbar is existing', () => {

        cy.visit('/');

        cy.get('.sf-toolbar-icon > .sf-toolbar-status').should('exist');
    })
});


describe('Shopware Administration', () => {

    it('Verify installed Shopware Version: ' + shopware.getVersion(), () => {

        adminAction.login();

        cy.contains('.sw-version__info', shopware.getVersion());
    })

    it('Dockware Sample Plugin is installed', () => {

        adminAction.login();

        cy.get('.sw-extension > span.sw-admin-menu__navigation-link > .sw-admin-menu__navigation-link-label').click();
        cy.get('.sw-extension-my-extensions > .sw-admin-menu__navigation-link > .sw-admin-menu__navigation-link-label').click();

        const rowDockwarePlugin = ':nth-child(2) > .sw-meteor-card__content > .sw-meteor-card__content-wrapper';

        cy.contains(rowDockwarePlugin, 'Dockware Sample Plugin', {timeout: 10000});
        cy.contains(rowDockwarePlugin, 'Installed', {timeout: 10000});
    })

})
