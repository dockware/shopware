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

        cy.contains('with Shopware');
    })

    it('Shopware Storefront navigation is working', () => {

        cy.visit('/');

        cy.get('.nav-item-a515ae260223466f8e37471d279e6406-link > .main-navigation-link-text').click();

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

        if (shopware.isVersionGreaterEqual('6.7.15.0')) {
            // since 6.7.15.0 the version is only visible in the user actions menu
            cy.contains('[id^="reka-dropdown-menu-trigger"]', /admin/i, {timeout: 10000}).click();
            cy.contains('.sw-admin-menu__user-actions-menu .sw-version__info', shopware.getVersion());
        } else {
            cy.contains('.sw-version__info', shopware.getVersion());
        }
    })

    it('Dockware Sample Plugin is installed', () => {

        adminAction.login();

        // wait until the login is done, before navigating directly to the extension listing
        cy.get('.sw-admin-menu', {timeout: 10000}).should('be.visible');
        cy.visit('/admin#/sw/extension/my-extensions/listing/app');

        cy.contains('.sw-extension-card-base', 'Dockware Sample Plugin', {timeout: 10000})
            .should('contain', 'Installed');
    })

})
