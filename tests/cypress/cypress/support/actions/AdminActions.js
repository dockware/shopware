export default class AdminActions {

    /**
     *
     */
    login() {
        cy.visit('/admin');
        cy.get('#sw-field--username', {timeout: 10000}).type('admin');
        cy.get('#sw-field--password', {timeout: 10000}).type('shopware');
        cy.get('.mt-button,.sw-button').click();
    }

}
